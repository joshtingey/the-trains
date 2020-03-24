#! /bin/bash

if [ -n "${POSTGRES_USER}" ]; 
then
  echo 'POSTGRES_USER was set'
else
  echo 'POSTGRES_USER was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${POSTGRES_PASSWORD}" ]; 
then
  echo 'POSTGRES_PASSWORD was set'
else
  echo 'POSTGRES_PASSWORD was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${POSTGRES_DB}" ]; 
then
  echo 'POSTGRES_DB was set'
else
  echo 'POSTGRES_DB was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${TRANSPORTAPI_ID}" ]; 
then
  echo 'TRANSPORTAPI_ID was set'
else
  echo 'TRANSPORTAPI_ID was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${TRANSPORTAPI_KEY}" ]; 
then
  echo 'TRANSPORTAPI_KEY was set'
else
  echo 'TRANSPORTAPI_KEY was not set'
  exit 1 # terminate and indicate error
fi