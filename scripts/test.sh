#! /bin/bash

if [ -n "${MONGO_INITDB_ROOT_USERNAME}" ]; 
then
  echo 'MONGO_INITDB_ROOT_USERNAME was set'
else
  echo 'MONGO_INITDB_ROOT_USERNAME was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${MONGO_INITDB_ROOT_PASSWORD}" ]; 
then
  echo 'MONGO_INITDB_ROOT_PASSWORD was set'
else
  echo 'MONGO_INITDB_ROOT_PASSWORD was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${SERVER}" ]; 
then
  echo 'SERVER was set'
else
  echo 'SERVER was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${CERTIFICATE_AUTHORITY_DATA}" ]; 
then
  echo 'CERTIFICATE_AUTHORITY_DATA was set'
else
  echo 'CERTIFICATE_AUTHORITY_DATA was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${USER_TOKEN}" ]; 
then
  echo 'USER_TOKEN was set'
else
  echo 'USER_TOKEN was not set'
  exit 1 # terminate and indicate error
fi