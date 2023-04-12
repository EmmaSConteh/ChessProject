# Team Ocelot
# SEG Small Group (Chess) Project

## Team Members:
- Ravshanbek (Rav) Rozukulov (k20016722)
- Fathima (JD) Jamal-Deen (k1922032)
- Nathan Essel (k2036035)
- Emma Conteh (k20045772)
- Aadit Jain (k20081379)

## Deployed Site: 
Deployed app: https://floating-spire-81612.herokuapp.com  
Administrative interface: https://floating-spire-81612.herokuapp.com/admin/

## Significant reused code
### Creating a 'User' model without username

To create a user model that uses email address instead of username to identify different users the following resources were used:
#### Article 'Django: Custom User model without username field (and using email in place of it)' on Personal Blog of Readul Hasan Chayan (Heemayl)
Link to the article: https://heemayl.net/posts/django-custom-user-model-without-username-field-and-using-email-in-place-of-it/

- 43 lines defining custom UserManager for the created User model
- 3 lines defining the actual User model

#### Django documentation section for "[Specifying a custom user model](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#specifying-a-custom-user-model)" and corresponding "[Full example](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#a-full-example)"

- 12 lines defining the actual User model
- 70 lines in admin.py file defining the following classes: __UserAdmin__, __UserChangeForm__, __UserCreationForm__
