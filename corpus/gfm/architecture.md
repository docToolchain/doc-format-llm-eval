# Parcel Tracker: Architecture Documentation

## Introduction

Parcel Tracker shows customers where their parcel is.
Carriers push status events; customers query the current status.

## Building Block View

The system consists of the Tracker API, the Event Ingest service and a PostgreSQL database.

## Deployment View

The Parcel Tracker API runs as three replicas behind an NGINX load balancer.
Each replica keeps a pool of 20 database connections to the primary PostgreSQL instance.

The Event Ingest service runs as a single instance and writes to the same database.
