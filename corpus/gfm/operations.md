# Parcel Tracker: Operations Handbook

## Runtime Setup

The Parcel Tracker API runs as three replicas behind an NGINX load balancer.
Each replica keeps a pool of 20 database connections to the primary PostgreSQL instance.

## Scaling

Scale the Tracker API horizontally when the p95 latency exceeds 300 ms.
Check the database connection limit before adding replicas.
