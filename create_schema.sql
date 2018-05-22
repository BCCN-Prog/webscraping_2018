CREATE TABLE "dailyperiodprediction" (
  "id" SERIAL CONSTRAINT "pk_dailyperiodprediction" PRIMARY KEY,
  "website" TEXT NOT NULL,
  "city" TEXT NOT NULL,
  "date_of_acquisition" TEXT NOT NULL,
  "date_for_which_weather_is_predicted" TEXT NOT NULL,
  "temperature" DOUBLE PRECISION NOT NULL,
  "wind_speed" DOUBLE PRECISION,
  "precipitation_per" DOUBLE PRECISION,
  "precipitation_l" DOUBLE PRECISION,
  "wind_direction" VARCHAR(3) NOT NULL,
  "condition" TEXT NOT NULL
);

CREATE TABLE "dailyprediction" (
  "id" SERIAL CONSTRAINT "pk_dailyprediction" PRIMARY KEY,
  "website" TEXT NOT NULL,
  "city" TEXT NOT NULL,
  "date_of_aquisition" TEXT NOT NULL,
  "date_for_which_weather_is_predicted" TEXT NOT NULL,
  "temperature_max" DOUBLE PRECISION NOT NULL,
  "temperature_min" DOUBLE PRECISION NOT NULL,
  "wind_speed" DOUBLE PRECISION,
  "humidity" DOUBLE PRECISION,
  "precipation_per" DOUBLE PRECISION,
  "precipation_l" DOUBLE PRECISION,
  "wind_direction" VARCHAR(3),
  "condition" TEXT,
  "snow" DOUBLE PRECISION,
  "uvi" BIGINT
);

CREATE TABLE "hourlyprediction" (
  "id" SERIAL CONSTRAINT "pk_hourlyprediction" PRIMARY KEY,
  "website" TEXT NOT NULL,
  "city" TEXT NOT NULL,
  "date_of_acquisition" TEXT NOT NULL,
  "date_for_which_weather_is_predicted" TEXT NOT NULL,
  "temperature" DOUBLE PRECISION NOT NULL,
  "wind_speed" DOUBLE PRECISION,
  "humidity" DOUBLE PRECISION,
  "precipitation_per" DOUBLE PRECISION,
  "precipitation_l" DOUBLE PRECISION,
  "wind_direction" VARCHAR(3) NOT NULL,
  "condition" TEXT NOT NULL,
  "snow" DOUBLE PRECISION,
  "uvi" BIGINT
)