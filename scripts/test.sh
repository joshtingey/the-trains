#! /bin/bash

if [ -n "${DB_USER}" ]; 
then
  echo 'DB_USER was set'
else
  echo 'DB_USER was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${DB_PASS}" ]; 
then
  echo 'DB_PASS was set'
else
  echo 'DB_PASS was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${DB_NAME}" ]; 
then
  echo 'DB_NAME was set'
else
  echo 'DB_NAME was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${NR_USER}" ]; 
then
  echo 'NR_USER was set'
else
  echo 'NR_USER was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${NR_PASS}" ]; 
then
  echo 'NR_PASS was set'
else
  echo 'NR_PASS was not set'
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