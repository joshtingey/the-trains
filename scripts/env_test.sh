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

if [ -n "${DATABASE_URL}" ]; 
then
  echo 'DATABASE_URL was set'
else
  echo 'DATABASE_URL was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${NETWORK_RAIL_USER}" ]; 
then
  echo 'NETWORK_RAIL_USER was set'
else
  echo 'NETWORK_RAIL_USER was not set'
  exit 1 # terminate and indicate error
fi

if [ -n "${NETWORK_RAIL_PASS}" ]; 
then
  echo 'NETWORK_RAIL_PASS was set'
else
  echo 'NETWORK_RAIL_PASS was not set'
  exit 1 # terminate and indicate error
fi