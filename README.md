# glassbank

A family banking app API. This is currently used in production by my family for managing finances.
Here are some notable features:

- Transaction epochs (a UUID could've been used too) to ensure transfers aren't performed multiple times.
- Django ORM transactions to ensure atomicity of transactions. Previous balances also stored for additonal safety.
- A currency conversion API is used to allow for GBP and EUR transactions.
- The Firebase API is used to push notifications to devices about transactions and requests.

## Usage

Clone the project:

```
$ git clone https://github.com/JohnGlass97/glassbank.git
```

Enter the root directory and install dependencies:

```
cd glassbank
pipenv install
```

Generate a secret key with the following command:

```
pipenv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Create an `.env` file at the project root with the following contents:

```
DJANGO_SECRET_KEY=<GENERATED_SECRET_KEY>
```

Perform db migrations and start the server:

```
pipenv run python manage.py migrate
pipenv run python manage.py runserver
```

## State of the project

This was built specifically for use by my family, so more work would be needed to generalise it for use by anyone.
Here are some improvements that could be made:

- Code documentation - proper Django structuring conventions are used, but the code is not well documented.
- Adding tests
- Generalisation to multiple separate families
