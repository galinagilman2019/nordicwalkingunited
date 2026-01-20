#!/bin/bash

# Name of the final zip
ZIP_NAME="PP_project.zip"

# Remove old zip parts if any
rm -f ${ZIP_NAME}*

# Create zip split into 50MB parts, excluding large or unnecessary folders
zip -r -s 50m $ZIP_NAME PP \
  -x "PP/venv/*" \
     "PP/node_modules/*" \
     "PP/media/*" \
     "PP/uploads/*" \
     "PP/staticfiles/*" \
     "PP/temp/*" \
     "*.pyc" \
     "__pycache__/*"

echo "✅ Project split into chunks successfully:"
ls -lh ${ZIP_NAME}*
