#!/bin/bash
# Prediction Pipeline Script

echo "================================"
echo "Home Credit Prediction Pipeline"
echo "================================"

# Check if input file is provided
if [ -z "$1" ]; then
    echo "Usage: ./predict_pipeline.sh <input_file> [output_file]"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_FILE=${2:-"data/predictions/predictions.csv"}

echo "Input file: $INPUT_FILE"
echo "Output file: $OUTPUT_FILE"

# Run predictions
echo "\nMaking predictions..."
python src/inference/predict.py --input "$INPUT_FILE" --output "$OUTPUT_FILE"

echo "\n================================"
echo "Predictions saved to: $OUTPUT_FILE"
echo "================================"
