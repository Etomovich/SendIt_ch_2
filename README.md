[![Coverage Status](https://coveralls.io/repos/github/Etomovich/SendIt_ch_2/badge.svg?branch=develop1)](https://coveralls.io/github/Etomovich/SendIt_ch_2?branch=develop1)[![Build Status](https://travis-ci.org/Etomovich/SendIt_ch_2.svg?branch=develop1)](https://travis-ci.org/Etomovich/SendIt_ch_2.svg?branch=develop1)

**SEND IT COURIER SERVICE** 

SendIT is a courier service that helps users deliver parcels to different destinations. It allows users to place orders of where they want their parcels to be delivered to from anywhere. Once a parcel is submitted to the station by the client or other arranged means, the user can pay and set the destination of where they want their parcel to go from where ever they may be.

**Specifications**

The SendIt API is a token based system. A user can gain access to the system by registering and the password is then hashed. When logging in a user is then given a token to use to get acces to any page available. 

**Features**
1. A user can register and login.
1. An admin can fetch all users.
1. An admin or the owner of the account can delete a user.
1. An admin or the owner of the account can edit particular details of the user and others details are 
restricted. For example a user if not an admin cannot edit the role of the user.
1. An admin can record a parcel submission.
1. A user can cancel a parcel delivery order.
1. An admin can edit the details of a parcel delivery order.
1. An admin can change the parcel destination.
1. A user can view the present location of his/her parcel.
1. An admin can change the status of a parcel.

**Database**
Swith to postgres account (in terminal)

`sudo su - postgres`

Run PostgreSQL command line client.

`psql`

Create a database user with a password.

`psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to postgres;" -U postgres`

`psql -c "ALTER USER postgres WITH PASSWORD '1234';" -U postgres`

Create a database instance.

`psql -c 'CREATE DATABASE sendit_db' -U postgres`

Create the test database instance.

`psql -c 'CREATE DATABASE sendit_test_db' -U postgres`



**Installation**

1. `git clone` the repository
1. create a virtual environment `virtualenv env`
1. Create a `.env` file with the following exports:

    `export PAGINATE_BASE_URL="https://etomovich-sendit.herokuapp.com"`

    `export DB_URL="dbname='sendit_db' host='localhost' user='postgres' port='5432' password='1234'"`

    `export DB_URL="dbname='sendit_test_db' host='localhost' user='postgres' port='5432' password='1234'"`
    
1. Activate the environment source `env\bin\activate`
1. pip install requirements by running `pip install -r requirements.txt`
1. run the server `python execute.py`

