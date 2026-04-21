/**
 * Geolocation utilities for capturing user's current location
 * Uses browser's Geolocation API and reverse geocoding
 */

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
  address?: string;
  timestamp: Date;
}

export interface GeolocationError {
  code: number;
  message: string;
}

/**
 * Request user's current location
 */
export const getUserLocation = (): Promise<LocationData> => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject({
        code: 0,
        message: "Geolocation is not supported by this browser",
      });
      return;
    }

    const options = {
      enableHighAccuracy: true, // Use GPS if available
      timeout: 10000,
      maximumAge: 0, // Don't use cached position
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date(position.timestamp),
        });
      },
      (error) => {
        let message = "An unknown error occurred";
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = "Location permission denied. Please enable location access in your browser settings.";
            break;
          case error.POSITION_UNAVAILABLE:
            message = "Location information is unavailable.";
            break;
          case error.TIMEOUT:
            message = "Location request timed out. Please try again.";
            break;
        }

        reject({
          code: error.code,
          message: message,
        });
      },
      options
    );
  });
};

/**
 * Watch user's location (for real-time tracking)
 */
export const watchUserLocation = (
  onSuccess: (location: LocationData) => void,
  onError: (error: GeolocationError) => void,
  options?: PositionOptions
) => {
  if (!navigator.geolocation) {
    onError({
      code: 0,
      message: "Geolocation is not supported by this browser",
    });
    return null;
  }

  const defaultOptions: PositionOptions = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0,
    ...options,
  };

  const watchId = navigator.geolocation.watchPosition(
    (position) => {
      onSuccess({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date(position.timestamp),
      });
    },
    (error) => {
      let message = "An unknown error occurred";
      
      switch (error.code) {
        case error.PERMISSION_DENIED:
          message = "Location permission denied";
          break;
        case error.POSITION_UNAVAILABLE:
          message = "Location information is unavailable";
          break;
        case error.TIMEOUT:
          message = "Location request timed out";
          break;
      }

      onError({
        code: error.code,
        message: message,
      });
    },
    defaultOptions
  );

  return watchId;
};

/**
 * Stop watching location
 */
export const stopWatchingLocation = (watchId: number) => {
  if (typeof watchId === "number") {
    navigator.geolocation.clearWatch(watchId);
  }
};

/**
 * Get reverse geocoded address from coordinates (using OpenStreetMap Nominatim)
 */
export const getAddressFromCoordinates = async (
  latitude: number,
  longitude: number
): Promise<string> => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`,
      {
        headers: {
          "User-Agent": "GrievanceSystem/1.0",
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to get address");
    }

    const data = await response.json();
    return data.address?.display_name || `${latitude}, ${longitude}`;
  } catch (error) {
    console.error("Error getting address:", error);
    // Return coordinates as fallback
    return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
  }
};

/**
 * Validate coordinates
 */
export const validateCoordinates = (
  latitude: number,
  longitude: number
): boolean => {
  return (
    typeof latitude === "number" &&
    typeof longitude === "number" &&
    latitude >= -90 &&
    latitude <= 90 &&
    longitude >= -180 &&
    longitude <= 180
  );
};

/**
 * Calculate distance between two coordinates (Haversine formula)
 * Returns distance in kilometers
 */
export const calculateDistance = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const R = 6371; // Earth's radius in kilometers

  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return Math.round(distance * 100) / 100; // Round to 2 decimal places
};

/**
 * Format coordinates for display
 */
export const formatCoordinates = (
  latitude: number,
  longitude: number,
  precision: number = 6
): string => {
  return `${latitude.toFixed(precision)}, ${longitude.toFixed(precision)}`;
};

/**
 * Check if browser supports geolocation
 */
export const isGeolocationSupported = (): boolean => {
  return !!navigator.geolocation;
};

/**
 * Get human readable accuracy description
 */
export const getAccuracyDescription = (accuracy: number): string => {
  if (accuracy < 10) {
    return "Very accurate (< 10m)";
  } else if (accuracy < 50) {
    return "Accurate (10-50m)";
  } else if (accuracy < 100) {
    return "Moderately accurate (50-100m)";
  } else if (accuracy < 500) {
    return "Less accurate (100-500m)";
  } else {
    return "Low accuracy (> 500m)";
  }
};
