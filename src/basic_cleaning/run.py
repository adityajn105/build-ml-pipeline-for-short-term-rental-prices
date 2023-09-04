#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb

import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    #getting input artifact
    logger.info("Downloading artifact file to process")
    artifact  = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact)

    #drop outliers
    logger.info("Drop outliers")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    #dropping out of bound geolocations.
    logger.info("Dropping rows with improper geolocation")
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    #drop null values
    logger.info("Dropping null values")
    df = df.dropna()

    #save the dataframe
    logger.info("Saving the df as csv")
    file_name = "clean_sample.csv"
    df.to_csv(file_name, index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file(file_name)
    logger.info("Logging artifact")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name for input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of processed artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price for Price column",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price for Price column",
        required=True
    )


    args = parser.parse_args()

    go(args)
