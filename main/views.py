from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls.base import reverse

from .forms import RegistrationForm, SignInForm, ProfileForm
from .models import User, UserAddress
from .tasks import save_to_mongodb, update_mongodb_data, send_email

import logging
import pymongo

logger = logging.getLogger('general')

mongodb_client = pymongo.MongoClient(f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_CLUSTER_ADDRESS}")

def home(request):
    title = 'Providers'
    db = mongodb_client[settings.MONGODB_DATABASE_NAME]
    collection = db[settings.MONGODB_COLLECTION]
    if request.user.is_authenticated:
        user_type = request.user.user_type
        longitude = request.user.location[0]['lon']
        latitude = request.user.location[0]['lat']
        if user_type == 'provider':
            title = 'Consumers'
            get_users = collection.aggregate(
                [
                    {
                        '$geoNear':
                        {
                            'near':
                            {
                                'type': "Point",
                                'coordinates': [
                                    float(longitude),
                                    float(latitude)
                                ]
                            },
                            'distanceField': "distance"
                        }
                    },
                    {
                        '$match': {
                            'user_type': 'consumer'
                        }
                    }
                ]
            )
        else:
            get_users = collection.aggregate(
                [
                    {
                        '$geoNear':
                        {
                            'near':
                            {
                                'type': "Point",
                                'coordinates': [
                                    float(longitude),
                                    float(latitude)
                                ]
                            },
                            'distanceField': "distance"
                        }
                    },
                    {
                        '$match': {
                            'user_type': 'provider'
                        }
                    }
                ]
            )
    else:
        get_users = collection.find({'user_type': 'provider'})
    return render(request, 'home.html', {'users': get_users, 'result_title': title})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'GET':
        register_form = RegistrationForm()
        return render(request, 'registration.html', {'form': register_form})
    elif request.method == 'POST':
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            provider_type = register_form.cleaned_data['provider_type']
            consumer_type = register_form.cleaned_data['consumer_type']
            phone_number = register_form.cleaned_data['phone_number']
            location = register_form.cleaned_data['location']
            longitude, latitude = location.strip().split(',')
            register_form.cleaned_data['location'] = [{'lon': float(longitude), 'lat': float(latitude)}]
            register_form.cleaned_data['username'] = phone_number

            if provider_type and consumer_type:
                register_form.add_error(None, error='Please choose options from provider or consumer only')

            if not provider_type and not consumer_type:
                register_form.add_error(None, error='Please choose atleast one type of option to register')
                
            if register_form.errors:
                return render(request, 'registration.html', {"form": register_form})

            # Validation complete, save data

            oxygen = False
            remdesivir = False
            plasma = False
            user_type = 'consumer'

            if provider_type:
                user_type = 'provider'

                if "oxygen" in provider_type:
                    oxygen = True

                if "remdesivir" in provider_type:
                    remdesivir = True

                if "plasma" in provider_type:
                    plasma = True
            
            if consumer_type:
                user_type = 'consumer'

                if "oxygen" in consumer_type:
                    oxygen = True

                if "remdesivir" in consumer_type:
                    remdesivir = True

                if "plasma" in consumer_type:
                    plasma = True

            try:
                user = register_form.save(commit=False)
                user.email = register_form.cleaned_data['email']
                user.phone_no = register_form.cleaned_data['phone_number']
                user.oxygen = oxygen
                user.remdesivir = remdesivir
                user.plasma = plasma
                user.user_type = user_type
                user.location = [{"lat": float(latitude), "lon": float(longitude)}]
                user.save()
                logger.info("User successfully registered")
                # Add to MongoDB
                save_to_mongodb.apply_async(kwargs={'user_id': user.id})
            except Exception as ex:
                logger.error("Failed to Register User")
                logger.error(ex)
                if register_form.errors:
                    return render(request, 'registration.html', {"form": register_form})
                messages.error(request, message="Something went wrong please register again")
                return redirect('register')
            send_email.apply_async(kwargs={'user_id': user.id})
            messages.success(request, message="Registration successful. You can login now.")
            return redirect('login')
        else:
            logger.error(register_form.errors)
        return render(request, 'registration.html', {"form": register_form})


class Login(LoginView):

    template_name = 'login.html'
    form_class = SignInForm
    redirect_authenticated_user = True

    def form_valid(self, form) -> HttpResponse:
        super_form_valid = super().form_valid(form)
        if self.request.user.is_authenticated:
            check_user = User.objects.filter(id=self.request.user.id).first()
            if not check_user.first_name:
                details_missing_message = f"Please update your personal details <a class='underline' href='{reverse('profile')}'>here</a>."
                details_incomplete_message = f"People might not call you if your details are incomplete."
                messages.info(self.request, message=details_missing_message, extra_tags='safe text-white')
                messages.warning(self.request, message=details_incomplete_message)
        return super_form_valid

@login_required
def profile(request):
    if request.method == 'GET':
        profile_form = ProfileForm()
        provider_type = []
        consumer_type = []
        if request.user.user_type == 'provider':
            if request.user.oxygen:
                provider_type.append('oxygen')
            if request.user.remdesivir:
                provider_type.append('remdesivir')
            if request.user.plasma:
                provider_type.append('plasma')

        if request.user.user_type == 'consumer':
            if request.user.oxygen:
                consumer_type.append('oxygen')
            if request.user.remdesivir:
                consumer_type.append('remdesivir')
            if request.user.plasma:
                consumer_type.append('plasma')

        # Get Address
        get_address = UserAddress.objects.filter(user=request.user).first()
        profile_form.initial = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_no": request.user.phone_no,
            "email": request.user.email,
            "location": ",".join([str(request.user.location[0]["lon"]), str(request.user.location[0]["lat"])]),
            "address_line_1": get_address.address_line_1 if get_address else "",
            "address_line_2": get_address.address_line_2 if get_address else "",
            "state": get_address.state if get_address else "",
            "city": get_address.city if get_address else "",
            "pincode": get_address.pincode if get_address else "",
            "provider_type": provider_type, 
            "consumer_type": consumer_type
            }
        return render(request, 'profile_page.html', {"form": profile_form})
    else:
        profile_form = ProfileForm(request.POST, user_id=request.user.id)
        if profile_form.is_valid():
            provider_type = profile_form.cleaned_data['provider_type']
            consumer_type = profile_form.cleaned_data['consumer_type']
            phone_number = profile_form.cleaned_data['phone_no']
            location = profile_form.cleaned_data['location']
            longitude, latitude = location.strip().split(',')
            profile_form.cleaned_data['location'] = [{'lon': float(longitude), 'lat': float(latitude)}]
            profile_form.cleaned_data['username'] = phone_number

            if provider_type and consumer_type:
                profile_form.add_error(None, error='Please choose options from provider or consumer only')

            if not provider_type and not consumer_type:
                profile_form.add_error(None, error='Please choose atleast one type of option to register')
                
            if profile_form.errors:
                return render(request, 'profile_page.html', {"form": profile_form})

            # Validation complete, save data

            oxygen = False
            remdesivir = False
            plasma = False
            user_type = 'consumer'

            if provider_type:
                user_type = 'provider'

                if "oxygen" in provider_type:
                    oxygen = True

                if "remdesivir" in provider_type:
                    remdesivir = True

                if "plasma" in provider_type:
                    plasma = True
            
            if consumer_type:
                user_type = 'consumer'

                if "oxygen" in consumer_type:
                    oxygen = True

                if "remdesivir" in consumer_type:
                    remdesivir = True

                if "plasma" in consumer_type:
                    plasma = True

            try:
                user = User.objects.filter(id=request.user.id).first()
                user.first_name = profile_form.cleaned_data['first_name']
                user.last_name = profile_form.cleaned_data['last_name']
                user.email = profile_form.cleaned_data['email']
                user.phone_no = profile_form.cleaned_data['phone_no']
                user.oxygen = oxygen
                user.remdesivir = remdesivir
                user.plasma = plasma
                user.user_type = user_type
                user.location = [{"lat": float(latitude), "lon": float(longitude)}]
                user.save()
                # Get Address
                address = UserAddress.objects.filter(user=user).first()
                address_line_1 = profile_form.cleaned_data['address_line_1']
                address_line_2 = profile_form.cleaned_data['address_line_2']
                state = profile_form.cleaned_data['state']
                city = profile_form.cleaned_data['city']
                pincode = profile_form.cleaned_data['pincode']
                if address:
                    address.address_line_1 = address_line_1
                    address.address_line_2 = address_line_2
                    address.state = state
                    address.city = city
                    address.pincode = pincode
                    address.save()
                else:
                    address = UserAddress.objects.create(
                        address_line_1=address_line_1,
                        address_line_2=address_line_2,
                        state=state,
                        city=city,
                        pincode=pincode,
                        user=user
                        )
                    
                logger.info("User updated successfully")
                # Add to MongoDB
                update_mongodb_data.apply_async(kwargs={'user_id': user.id})
            except Exception as ex:
                logger.error("Failed to Update User")
                logger.error(ex)
                if profile_form.errors:
                    return render(request, 'profile_page.html', {"form": profile_form})
                messages.error(request, "Something went wrong please try again")
                return redirect('profile')
            messages.success(request, "Profile updated successfully")
            return redirect('profile')
        else:
            messages.error(request, "Something went wrong please try again")
            logger.error("Failed to update User profile")
        return render(request, 'profile_page.html', {"form": profile_form})


def oxygen(request):
    if request.method == 'GET':
        title = 'Providers'
        db = mongodb_client[settings.MONGODB_DATABASE_NAME]
        collection = db[settings.MONGODB_COLLECTION]
        if request.user.is_authenticated:
            user_type = request.user.user_type
            longitude = request.user.location[0]['lon']
            latitude = request.user.location[0]['lat']
            if user_type == 'provider':
                title = 'Consumers'
                get_users = collection.aggregate(
                    [
                        {
                            '$geoNear':
                            {
                                'near':
                                {
                                    'type': "Point",
                                    'coordinates': [
                                        float(longitude),
                                        float(latitude)
                                    ]
                                },
                                'distanceField': "distance"
                            }
                        },
                        {
                            '$match': {
                                'user_type': 'consumer',
                                'oxygen': True
                            }
                        }
                    ]
                )
            else:
                get_users = collection.aggregate(
                    [
                        {
                            '$geoNear':
                            {
                                'near':
                                {
                                    'type': "Point",
                                    'coordinates': [
                                        float(longitude),
                                        float(latitude)
                                    ]
                                },
                                'distanceField': "distance"
                            }
                        },
                        {
                            '$match': {
                                'user_type': 'provider',
                                'oxygen': True
                            }
                        }
                    ]
                )
        else:
            get_users = collection.find({'user_type': 'provider', 'oxygen': True})
    return render(request, 'oxygen.html', {'users': get_users, 'result_title': title})


def remdesivir(request):
    if request.method == 'GET':
        title = 'Providers'
        db = mongodb_client[settings.MONGODB_DATABASE_NAME]
        collection = db[settings.MONGODB_COLLECTION]
        if request.user.is_authenticated:
            user_type = request.user.user_type
            longitude = request.user.location[0]['lon']
            latitude = request.user.location[0]['lat']
            if user_type == 'provider':
                title = 'Consumers'
                get_users = collection.aggregate(
                    [
                        {
                            '$geoNear':
                            {
                                'near':
                                {
                                    'type': "Point",
                                    'coordinates': [
                                        float(longitude),
                                        float(latitude)
                                    ]
                                },
                                'distanceField': "distance"
                            }
                        },
                        {
                            '$match': {
                                'user_type': 'consumer',
                                'remdesivir': True
                            }
                        }
                    ]
                )
            else:
                get_users = collection.aggregate(
                    [
                        {
                            '$geoNear':
                            {
                                'near':
                                {
                                    'type': "Point",
                                    'coordinates': [
                                        float(longitude),
                                        float(latitude)
                                    ]
                                },
                                'distanceField': "distance"
                            }
                        },
                        {
                            '$match': {
                                'user_type': 'provider',
                                'remdesivir': True
                            }
                        }
                    ]
                )
        else:
            get_users = collection.find({'user_type': 'provider', 'remdesivir': True})
    return render(request, 'remdesivir.html', {'users': get_users, 'result_title': title})


def plasma(request):
    if request.method == 'GET':
        title = 'Providers'
        db = mongodb_client[settings.MONGODB_DATABASE_NAME]
        collection = db[settings.MONGODB_COLLECTION]
        if request.user.is_authenticated:
            user_type = request.user.user_type
            longitude = request.user.location[0]['lon']
            latitude = request.user.location[0]['lat']
            if user_type == 'provider':
                title = 'Consumers'
                get_users = collection.aggregate(
                    [
                        {
                            '$geoNear':
                            {
                                'near':
                                {
                                    'type': "Point",
                                    'coordinates': [
                                        float(longitude),
                                        float(latitude)
                                    ]
                                },
                                'distanceField': "distance"
                            }
                        },
                        {
                            '$match': {
                                'user_type': 'consumer',
                                'plasma': True
                            }
                        }
                    ]
                )
            else:
                get_users = collection.aggregate(
                    [
                        {
                            '$geoNear':
                            {
                                'near':
                                {
                                    'type': "Point",
                                    'coordinates': [
                                        float(longitude),
                                        float(latitude)
                                    ]
                                },
                                'distanceField': "distance"
                            }
                        },
                        {
                            '$match': {
                                'user_type': 'provider',
                                'plasma': True
                            }
                        }
                    ]
                )
        else:
            get_users = collection.find({'user_type': 'provider', 'plasma': True})
    return render(request, 'plasma.html', {'users': get_users, 'result_title': title})

def thank_you(request):
    if request.method == 'GET':
        if "just_registered" in request.session and request.session["just_registered"]:
            del request.session["just_registered"]
            return render(request, "thank_you.html")
        else:
            return redirect('home')
    else:
        return redirect('home')
