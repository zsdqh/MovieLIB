#!/bin/bash
echo "Verifying email"
awslocal ses verify-email-identity --email "$EMAIL"
echo "Verifying done for $EMAIL"
