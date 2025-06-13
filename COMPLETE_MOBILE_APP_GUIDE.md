# 📱 Mobile App Integration Guide - React Native + Expo + Firebase
## Location-Based Game Mobile Application

> **🎯 Goal**: Create a React Native app with Expo that integrates with the Django GeoDjango backend and Firebase FCM for push notifications.

---

## 🎯 **GitHub Copilot Instructions – React Native Game App (Expo + Expo Router)**

### 📦 **Project Structure Rules**
- Follow **modular architecture**
- Each screen goes under `/app/screens/`
- UI components go in `/app/components/`
- API requests are handled in `/app/services/`
- Global state is managed using **Zustand** in `/app/store/`
- Shared constants or helpers go in `/app/utils/`

### 🗺️ **Map and Location Handling**
- Use **react-native-maps** for Google Map
- Use **expo-location** for fetching current user location
- Represent zones as **grid-based tiles** on the map
- Color-code tiles based on ownership status:
  - **Gray** = unclaimed
  - **Blue** = mine
  - **Red** = enemy

### 🔐 **Authentication**
- Use **JWT tokens** from the backend
- Store token securely with **expo-secure-store**
- Authenticate all API requests using **Bearer tokens via Axios interceptors**

### ⚔️ **Game Logic (Frontend)**
- Allow check-in only if the user is **physically inside the zone**
- Disable check-in if zone is **already owned by user**
- Display **popup modals** on attack or check-in success/failure
- Pull leaderboard and zone status from backend via **REST endpoints**

### 🛠️ **API Requests**
- Use **axios** or **react-query** for API calls
- All API requests should be modular, written in `/app/services/api.js` or `/app/services/zoneService.js`
- **Error and loading states** must be handled cleanly with feedback to users

### 🔔 **Notifications**
- Use **expo-notifications**
- Register for push token on login, send it to the backend
- Listen for incoming notifications (e.g., zone under attack) and show modal alerts or push

### 🧪 **Testing**
- Use **jest-expo** for unit testing
- Keep logic-heavy components isolated for testability
- Screens and services should be tested independently

### ♻️ **Reusability & Maintainability**
- Break down complex screens into reusable components
- Keep state logic inside **Zustand** or isolated hooks
- Use enums or constants for statuses and colors (e.g., `OWNED`, `ENEMY`, `UNCLAIMED`)

### 🚀 **Deployment**
- Use **Expo EAS** for building and deploying OTA updates

---

## 🚀 Project Setup

### 1. Initialize Expo Project
```bash
npx create-expo-app LocationGameApp --template blank-typescript
cd LocationGameApp
```

### 2. Install Required Dependencies
```bash
# Core dependencies
npm install expo-router expo-notifications expo-device expo-constants
npm install react-native-maps expo-location expo-permissions
npm install axios @tanstack/react-query @tanstack/react-query-devtools
npm install firebase
npm install react-native-elements react-native-vector-icons
npm install expo-haptics zustand expo-secure-store

# Development dependencies
npm install --save-dev @types/react @types/react-native typescript
npm install --save-dev jest-expo @testing-library/react-native @testing-library/jest-native
```

### 3. Configure app.json
```json
{
  "expo": {
    "name": "Location Game",
    "slug": "location-game-app",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.yourcompany.locationgame",
      "config": {
        "googleMapsApiKey": "YOUR_GOOGLE_MAPS_API_KEY"
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.yourcompany.locationgame",
      "config": {
        "googleMaps": {
          "apiKey": "YOUR_GOOGLE_MAPS_API_KEY"
        }
      },
      "permissions": [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "RECEIVE_BOOT_COMPLETED",
        "VIBRATE"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      "expo-router",
      [
        "expo-notifications",
        {
          "icon": "./assets/notification-icon.png",
          "color": "#ffffff"
        }
      ],
      [
        "expo-location",
        {
          "locationAlwaysAndWhenInUsePermission": "This app needs access to location for the game map."
        }
      ]
    ],
    "scheme": "locationgame"
  }
}
```

---

## 🔥 Firebase Configuration

### 1. Create Firebase Services (`services/firebase.ts`)
```typescript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';
import Constants from 'expo-constants';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';

const firebaseConfig = {
  apiKey: Constants.expoConfig?.extra?.firebaseApiKey,
  authDomain: Constants.expoConfig?.extra?.firebaseAuthDomain,
  projectId: "location-game-backend",
  storageBucket: Constants.expoConfig?.extra?.firebaseStorageBucket,
  messagingSenderId: Constants.expoConfig?.extra?.firebaseMessagingSenderId,
  appId: Constants.expoConfig?.extra?.firebaseAppId
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export class FirebaseService {
  static async requestPermissions(): Promise<string | null> {
    if (!Device.isDevice) {
      console.log('Must use physical device for Push Notifications');
      return null;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return null;
    }

    const token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log('Push token:', token);
    return token;
  }

  static setupNotificationListeners(
    onNotificationReceived: (notification: any) => void,
    onNotificationResponse: (response: any) => void
  ) {
    // Handle notifications when app is in foreground
    Notifications.addNotificationReceivedListener(onNotificationReceived);

    // Handle notification tap
    Notifications.addNotificationResponseReceivedListener(onNotificationResponse);
  }
}

export default app;
```

### 2. Environment Configuration
Create `.env`:
```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
EXPO_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=location-game-backend.firebaseapp.com
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=location-game-backend.appspot.com
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
EXPO_PUBLIC_FIREBASE_APP_ID=your_app_id
```

---

## 🌐 API Integration

### 1. API Service (`services/api.ts`)
```typescript
import axios, { AxiosResponse } from 'axios';
import { useAuthStore } from '../store/authStore';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl || 'http://localhost:8000/api/v1';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { refreshToken } = useAuthStore.getState();
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          useAuthStore.getState().setAuth(
            useAuthStore.getState().user!,
            access,
            refreshToken
          );

          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        useAuthStore.getState().clearAuth();
        // Navigate to login screen
      }
    }

    return Promise.reject(error);
  }
);
```

### 2. Zone Service with React Query (`services/zoneService.ts`)
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import { Zone } from '../types/game';
import { useGameStore } from '../store/gameStore';

// Query keys
export const QUERY_KEYS = {
  zones: ['zones'] as const,
  zone: (id: number) => ['zones', id] as const,
  nearbyZones: (lat: number, lng: number) => ['zones', 'nearby', lat, lng] as const,
};

// Fetch all zones
export const useZones = () => {
  const setZones = useGameStore((state) => state.setZones);

  return useQuery({
    queryKey: QUERY_KEYS.zones,
    queryFn: async (): Promise<Zone[]> => {
      const response = await apiClient.get('/zones/');
      const zones = response.data.results;
      setZones(zones);
      return zones;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 20000, // Consider data fresh for 20 seconds
  });
};

// Fetch single zone
export const useZone = (id: number) => {
  return useQuery({
    queryKey: QUERY_KEYS.zone(id),
    queryFn: async (): Promise<Zone> => {
      const response = await apiClient.get(`/zones/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

// Check-in to zone
export const useCheckInZone = () => {
  const queryClient = useQueryClient();
  const updateZone = useGameStore((state) => state.updateZone);

  return useMutation({
    mutationFn: async ({
      zoneId,
      latitude,
      longitude
    }: {
      zoneId: number;
      latitude: number;
      longitude: number;
    }) => {
      const response = await apiClient.post('/zones/check-in/', {
        zone_id: zoneId,
        latitude,
        longitude,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Update local state
      updateZone(data.zone);

      // Invalidate and refetch zones
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.zones });
    },
  });
};
```

### 3. Attack Service (`services/attackService.ts`)
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import { Attack, AttackResponse } from '../types/game';
import { useGameStore } from '../store/gameStore';

export const ATTACK_QUERY_KEYS = {
  attacks: ['attacks'] as const,
  userAttacks: ['attacks', 'user'] as const,
  attackStats: ['attacks', 'stats'] as const,
};

// Attack zone mutation
export const useAttackZone = () => {
  const queryClient = useQueryClient();
  const { addAttack, updateZone } = useGameStore();

  return useMutation({
    mutationFn: async ({
      zoneId,
      latitude,
      longitude
    }: {
      zoneId: number;
      latitude: number;
      longitude: number;
    }): Promise<AttackResponse> => {
      const response = await apiClient.post('/attacks/', {
        zone_id: zoneId,
        latitude,
        longitude,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Add attack to local state
      addAttack(data.attack);

      // Update zone if captured
      if (data.zone_captured && data.zone) {
        updateZone(data.zone);
      }

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.zones });
      queryClient.invalidateQueries({ queryKey: ATTACK_QUERY_KEYS.attacks });
    },
  });
};

// Get attack history
export const useAttackHistory = () => {
  return useQuery({
    queryKey: ATTACK_QUERY_KEYS.userAttacks,
    queryFn: async (): Promise<Attack[]> => {
      const response = await apiClient.get('/attacks/?type=made');
      return response.data.results;
    },
  });
};
```

---

## 🏪 **State Management with Zustand**

### 1. Auth Store (`store/authStore.ts`)
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import * as SecureStore from 'expo-secure-store';
import { User } from '../types/user';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;

  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
  updateUser: (user: User) => void;
}

// Secure storage implementation for Zustand
const secureStorage = {
  getItem: async (name: string): Promise<string | null> => {
    try {
      return await SecureStore.getItemAsync(name);
    } catch {
      return null;
    }
  },
  setItem: async (name: string, value: string): Promise<void> => {
    try {
      await SecureStore.setItemAsync(name, value);
    } catch {
      // Handle error silently
    }
  },
  removeItem: async (name: string): Promise<void> => {
    try {
      await SecureStore.deleteItemAsync(name);
    } catch {
      // Handle error silently
    }
  },
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,

      setAuth: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          loading: false,
        }),

      clearAuth: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          loading: false,
        }),

      setLoading: (loading) => set({ loading }),

      updateUser: (user) => set({ user }),
    }),
    {
      name: 'auth-storage',
      storage: secureStorage,
    }
  )
);
```

### 2. Game Store (`store/gameStore.ts`)
```typescript
import { create } from 'zustand';
import { Zone, Attack } from '../types/game';

// Game constants
export const ZONE_STATUS = {
  UNCLAIMED: 'unclaimed',
  OWNED: 'owned',
  ENEMY: 'enemy',
} as const;

export const ZONE_COLORS = {
  [ZONE_STATUS.UNCLAIMED]: '#9E9E9E', // Gray
  [ZONE_STATUS.OWNED]: '#2196F3',     // Blue
  [ZONE_STATUS.ENEMY]: '#F44336',     // Red
} as const;

interface GameState {
  zones: Zone[];
  attacks: Attack[];
  userLocation: {
    latitude: number;
    longitude: number;
  } | null;
  selectedZone: Zone | null;

  // Actions
  setZones: (zones: Zone[]) => void;
  updateZone: (zone: Zone) => void;
  setAttacks: (attacks: Attack[]) => void;
  addAttack: (attack: Attack) => void;
  setUserLocation: (location: { latitude: number; longitude: number }) => void;
  setSelectedZone: (zone: Zone | null) => void;

  // Computed
  getZoneStatus: (zone: Zone, currentUserId?: number) => keyof typeof ZONE_STATUS;
  getZoneColor: (zone: Zone, currentUserId?: number) => string;
  getNearbyZones: (radius?: number) => Zone[];
}

export const useGameStore = create<GameState>((set, get) => ({
  zones: [],
  attacks: [],
  userLocation: null,
  selectedZone: null,

  setZones: (zones) => set({ zones }),

  updateZone: (updatedZone) =>
    set((state) => ({
      zones: state.zones.map((zone) =>
        zone.id === updatedZone.id ? updatedZone : zone
      ),
    })),

  setAttacks: (attacks) => set({ attacks }),

  addAttack: (attack) =>
    set((state) => ({
      attacks: [attack, ...state.attacks],
    })),

  setUserLocation: (location) => set({ userLocation: location }),

  setSelectedZone: (zone) => set({ selectedZone: zone }),

  getZoneStatus: (zone, currentUserId) => {
    if (!zone.owner) return ZONE_STATUS.UNCLAIMED;
    if (zone.owner === currentUserId) return ZONE_STATUS.OWNED;
    return ZONE_STATUS.ENEMY;
  },

  getZoneColor: (zone, currentUserId) => {
    const status = get().getZoneStatus(zone, currentUserId);
    return ZONE_COLORS[status];
  },

  getNearbyZones: (radius = 100) => {
    const { zones, userLocation } = get();
    if (!userLocation) return [];

    return zones.filter((zone) => {
      const distance = calculateDistance(
        userLocation.latitude,
        userLocation.longitude,
        zone.latitude,
        zone.longitude
      );
      return distance <= radius;
    });
  },
}));

// Utility function for distance calculation
function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}
```

---

## 🗺️ **Grid-Based Map Implementation**

### 1. Enhanced Game Map with Grid Tiles (`components/game/GameMap.tsx`)
```typescript
import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import MapView, { Region, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';
import * as Haptics from 'expo-haptics';
import { useZones } from '../../services/zoneService';
import { useGameStore } from '../../store/gameStore';
import { useAuthStore } from '../../store/authStore';
import { GAME_CONFIG } from '../../utils/constants';
import ZoneTile from './ZoneTile';

interface GameMapProps {
  onZonePress: (zone: Zone) => void;
}

const GameMap: React.FC<GameMapProps> = ({ onZonePress }) => {
  const mapRef = useRef<MapView>(null);
  const { user } = useAuthStore();
  const {
    zones,
    userLocation,
    setUserLocation,
    getZoneStatus,
    getZoneColor
  } = useGameStore();

  const [region, setRegion] = useState<Region | null>(null);
  const [mapReady, setMapReady] = useState(false);

  // Fetch zones with React Query
  const { data: fetchedZones, isLoading, error } = useZones();

  useEffect(() => {
    initializeLocation();
    const locationWatcher = watchUserLocation();

    return () => {
      if (locationWatcher) {
        locationWatcher.remove();
      }
    };
  }, []);

  const initializeLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Location access is required for the game');
        return;
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      const newLocation = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      };

      setUserLocation(newLocation);

      const initialRegion: Region = {
        ...newLocation,
        latitudeDelta: 0.01,
        longitudeDelta: 0.01,
      };
      setRegion(initialRegion);
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Failed to get your location');
    }
  };

  const watchUserLocation = () => {
    return Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.High,
        timeInterval: 5000, // Update every 5 seconds
        distanceInterval: 10, // Update if moved 10 meters
      },
      (location) => {
        setUserLocation({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
        });
      }
    );
  };

  const handleZonePress = (zone: Zone) => {
    if (!userLocation) {
      Alert.alert('Error', 'Unable to determine your location');
      return;
    }

    // Check if user is within interaction radius
    const distance = calculateDistance(
      userLocation.latitude,
      userLocation.longitude,
      zone.latitude,
      zone.longitude
    );

    if (distance > GAME_CONFIG.ZONE_INTERACTION_RADIUS) {
      Alert.alert(
        'Too Far Away',
        `You need to be within ${GAME_CONFIG.ZONE_INTERACTION_RADIUS}m of the zone to interact with it.`
      );
      return;
    }

    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    onZonePress(zone);
  };

  const renderZoneTiles = () => {
    if (!zones || !user) return null;

    return zones.map((zone) => {
      const status = getZoneStatus(zone, user.id);
      const color = getZoneColor(zone, user.id);
      const isNearby = userLocation ?
        calculateDistance(
          userLocation.latitude,
          userLocation.longitude,
          zone.latitude,
          zone.longitude
        ) <= GAME_CONFIG.ZONE_INTERACTION_RADIUS : false;

      return (
        <ZoneTile
          key={zone.id}
          zone={zone}
          status={status}
          color={color}
          isNearby={isNearby}
          onPress={() => handleZonePress(zone)}
        />
      );
    });
  };

  if (isLoading || !region) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load zones</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        provider={PROVIDER_GOOGLE}
        initialRegion={region}
        showsUserLocation={true}
        showsMyLocationButton={true}
        mapType="standard"
        onMapReady={() => setMapReady(true)}
        maxZoomLevel={18}
        minZoomLevel={10}
      >
        {mapReady && renderZoneTiles()}
      </MapView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
  },
});

export default GameMap;
```

### 2. Grid-Based Zone Tile Component (`components/game/ZoneTile.tsx`)
```typescript
import React from 'react';
import { Polygon } from 'react-native-maps';
import { Zone } from '../../types/game';
import { ZONE_STATUS } from '../../utils/constants';

interface ZoneTileProps {
  zone: Zone;
  status: keyof typeof ZONE_STATUS;
  color: string;
  isNearby: boolean;
  onPress: () => void;
}

const ZoneTile: React.FC<ZoneTileProps> = ({
  zone,
  status,
  color,
  isNearby,
  onPress
}) => {
  // Create a square grid tile around the zone coordinates
  const tileSize = 0.001; // Adjust for desired tile size
  const coordinates = [
    {
      latitude: zone.latitude - tileSize,
      longitude: zone.longitude - tileSize,
    },
    {
      latitude: zone.latitude - tileSize,
      longitude: zone.longitude + tileSize,
    },
    {
      latitude: zone.latitude + tileSize,
      longitude: zone.longitude + tileSize,
    },
    {
      latitude: zone.latitude + tileSize,
      longitude: zone.longitude - tileSize,
    },
  ];

  return (
    <Polygon
      coordinates={coordinates}
      fillColor={`${color}80`} // Add transparency
      strokeColor={color}
      strokeWidth={isNearby ? 3 : 1}
      tappable={true}
      onPress={onPress}
    />
  );
};

export default ZoneTile;
```

---

## 🖥️ **Django GeoDjango Backend API Integration**

> **Complete API Documentation for Mobile App Integration**
>
> This section provides comprehensive backend API documentation so GitHub Copilot can understand all available endpoints, request/response formats, authentication patterns, and integration requirements.

### 📋 **API Base Configuration**

```typescript
// API Configuration
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1', // Development
  // BASE_URL: 'https://your-backend.com/api/v1', // Production
  TIMEOUT: 10000,
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
};

// Authentication Headers
const getAuthHeaders = (token: string) => ({
  ...API_CONFIG.HEADERS,
  'Authorization': `Bearer ${token}`
});
```

### 🔐 **Authentication System**

#### **User Registration**
```typescript
// POST /api/v1/auth/register/
interface UserRegistrationRequest {
  username: string;
  email: string;
  password: string;
  push_token?: string; // Optional FCM token
}

interface UserRegistrationResponse {
  user: {
    id: number;
    username: string;
    email: string;
    level: number;
    xp: number;
    zones_owned: number;
    attack_power: number;
    created_at: string;
  };
  tokens: {
    access: string;
    refresh: string;
  };
}
```

#### **User Login**
```typescript
// POST /api/v1/auth/login/
interface UserLoginRequest {
  username: string;
  password: string;
  push_token?: string; // Optional FCM token
}

interface UserLoginResponse {
  user: {
    id: number;
    username: string;
    email: string;
    level: number;
    xp: number;
    zones_owned: number;
    attack_power: number;
  };
  tokens: {
    access: string;
    refresh: string;
  };
}
```

#### **Token Refresh**
```typescript
// POST /api/v1/auth/token/refresh/
interface TokenRefreshRequest {
  refresh: string;
}

interface TokenRefreshResponse {
  access: string;
  refresh?: string; // New refresh token if rotated
}
```

#### **User Profile**
```typescript
// GET /api/v1/auth/profile/
interface UserProfileResponse {
  id: number;
  username: string;
  email: string;
  level: number;
  xp: number;
  zones_owned: number;
  attack_power: number;
  push_token?: string;
  created_at: string;
  updated_at: string;
}
```

### 🗺️ **Zone Management System**

#### **Get All Zones**
```typescript
// GET /api/v1/zones/
interface ZoneListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Zone[];
}

interface Zone {
  id: string; // Grid-based ID like "zone_37774_-122419"
  latitude: number;
  longitude: number;
  owner_username?: string;
  is_claimed: boolean;
  claimed_at?: string;
  expires_at?: string;
  xp_value: number;
  defense_power: number;
}
```

#### **Get Nearby Zones**
```typescript
// GET /api/v1/zones/nearby/
interface NearbyZonesRequest {
  latitude: number;
  longitude: number;
  radius?: number; // Default: 1000 meters
}

interface NearbyZonesResponse {
  zones: Zone[];
  count: number;
  user_location: {
    latitude: number;
    longitude: number;
  };
}
```

#### **Get Zone Details**
```typescript
// GET /api/v1/zones/{zone_id}/
interface ZoneDetailResponse extends Zone {
  checkin_history: ZoneCheckIn[];
  attack_history: Attack[];
}
```

#### **Claim Zone**
```typescript
// POST /api/v1/zones/{zone_id}/claim/
interface ClaimZoneRequest {
  latitude: number;
  longitude: number;
}

interface ClaimZoneResponse {
  message: string;
  zone: Zone;
  xp_gained: number;
}
```

#### **Check Into Zone**
```typescript
// POST /api/v1/zones/{zone_id}/checkin/
interface CheckInRequest {
  latitude: number;
  longitude: number;
}

interface CheckInResponse {
  checkin: {
    id: number;
    user: string;
    zone: string;
    timestamp: string;
    success: boolean;
  };
  message: string;
}
```

#### **Get User's Zones**
```typescript
// GET /api/v1/zones/my-zones/
interface UserZonesResponse {
  zones: Zone[];
  count: number;
}
```

#### **Get Check-in History**
```typescript
// GET /api/v1/zones/checkin-history/
interface CheckInHistoryResponse {
  checkins: ZoneCheckIn[];
  count: number;
}

interface ZoneCheckIn {
  id: number;
  zone: string;
  timestamp: string;
  success: boolean;
  latitude: number;
  longitude: number;
}
```

### ⚔️ **Attack System**

#### **Attack Zone**
```typescript
// POST /api/v1/attacks/
interface AttackZoneRequest {
  zone_id: string;
  latitude: number;
  longitude: number;
}

interface AttackZoneResponse {
  attack: {
    id: number;
    attacker_username: string;
    defender_username?: string;
    zone_id: string;
    attacker_power: number;
    defender_power: number;
    result: 'success' | 'failed' | 'cooldown' | 'invalid';
    success: boolean;
    xp_gained: number;
    latitude: number;
    longitude: number;
    timestamp: string;
  };
  message: string;
}
```

#### **Get Attack History**
```typescript
// GET /api/v1/attacks/?type=made (default)
// GET /api/v1/attacks/?type=received
interface AttackHistoryResponse {
  attacks: AttackHistory[];
  count: number;
}

interface AttackHistory {
  id: number;
  opponent_username: string;
  zone_id: string;
  attacker_power: number;
  defender_power: number;
  result: string;
  success: boolean;
  xp_gained: number;
  timestamp: string;
}
```

#### **Get Attack Cooldowns**
```typescript
// GET /api/v1/attacks/cooldown/
interface AttackCooldownResponse {
  cooldowns: CooldownStatus[];
  count: number;
}

interface CooldownStatus {
  zone_id: string;
  last_attack: string;
  cooldown_until: string;
  is_on_cooldown: boolean;
}
```

#### **Get Attack Statistics**
```typescript
// GET /api/v1/attacks/stats/
interface AttackStatsResponse {
  attacks_made: number;
  attacks_won: number;
  attacks_lost: number;
  defenses_successful: number;
  defenses_failed: number;
  attack_success_rate: number;
  defense_success_rate: number;
  total_xp_gained: number;
}
```

### 🏆 **Leaderboard System**

#### **Get Leaderboard**
```typescript
// GET /api/v1/leaderboard/?category=xp (default)
// GET /api/v1/leaderboard/?category=zones
// GET /api/v1/leaderboard/?category=level
// GET /api/v1/leaderboard/?category=attacks
interface LeaderboardResponse {
  category: string;
  leaderboard: LeaderboardEntry[];
  count: number;
}

interface LeaderboardEntry {
  rank: number;
  username: string;
  level: number;
  score: number; // XP, zone count, attack count, etc.
  last_updated?: string;
}
```

#### **Get User Rankings**
```typescript
// GET /api/v1/leaderboard/my-rank/
interface UserRankResponse {
  user: string;
  ranks: UserRankCategory[];
}

interface UserRankCategory {
  category: string;
  rank: number;
  score: number;
  total_users: number;
  percentile: number;
}
```

#### **Get Leaderboard Statistics**
```typescript
// GET /api/v1/leaderboard/stats/
interface LeaderboardStatsResponse {
  total_users: number;
  total_zones: number;
  total_attacks: number;
  most_active_zone: string;
  top_player: string;
}
```

#### **Get User Detailed Stats**
```typescript
// GET /api/v1/leaderboard/stats/{username}/
interface DetailedUserStatsResponse {
  username: string;
  level: number;
  xp: number;
  zones_owned_count: number;
  attacks_made: number;
  attacks_won: number;
  defenses_made: number;
  defenses_won: number;
  attack_success_rate: number;
  defense_success_rate: number;
}
```

### 🔥 **Firebase FCM Integration**

#### **Register FCM Token**
```typescript
// POST /api/v1/auth/push-token/
interface FCMTokenRequest {
  push_token: string;
  device_type?: 'ios' | 'android' | 'web';
}

interface FCMTokenResponse {
  success: boolean;
  message: string;
}
```

#### **Firebase Notification Payloads**
```typescript
// Zone Attack Notification
interface ZoneAttackNotification {
  type: 'zone_attack';
  title: string;
  body: string;
  data: {
    zone_id: string;
    zone_name: string;
    attacker_id: string;
    attacker_name: string;
    attack_time: string;
  };
}

// Battle Result Notification
interface BattleResultNotification {
  type: 'battle_result';
  title: string;
  body: string;
  data: {
    zone_id: string;
    result: 'victory' | 'defeat';
    xp_gained: number;
    attacker_name: string;
    defender_name: string;
  };
}

// Zone Captured Notification
interface ZoneCapturedNotification {
  type: 'zone_captured';
  title: string;
  body: string;
  data: {
    zone_id: string;
    zone_name: string;
    xp_gained: number;
    new_zones_owned: number;
  };
}

// Level Up Notification
interface LevelUpNotification {
  type: 'level_up';
  title: string;
  body: string;
  data: {
    old_level: number;
    new_level: number;
    new_attack_power: number;
    bonus_xp: number;
  };
}
```

### 🚨 **Error Handling**

#### **Standard Error Response**
```typescript
interface APIErrorResponse {
  error: string;
  details?: string;
  field_errors?: Record<string, string[]>;
  status_code: number;
}

// Example Error Responses
interface ZoneErrorCodes {
  'Zone not found': 404;
  'You cannot attack your own zone': 400;
  'Zone is not claimed by anyone': 400;
  'You must be within 20m of the zone': 400;
  'Attack on cooldown. Try again in X minutes': 400;
  'Zone is already claimed by another player': 400;
  'Authentication required': 401;
  'Invalid latitude or longitude': 400;
}
```

### ⚙️ **Game Configuration Constants**

```typescript
// Game Configuration (from Django settings)
const GAME_CONFIG = {
  ZONE_CAPTURE_RADIUS_METERS: 20,
  ZONE_EXPIRY_HOURS: 24,
  ATTACK_COOLDOWN_MINUTES: 30,
  MAX_NEARBY_ZONES: 50,
  DEFAULT_ZONE_XP_VALUE: 10,
  DEFENDER_ADVANTAGE: 20, // Added to defense power
  GRID_SIZE: 0.001, // Degrees for zone grid
  MAX_USER_LEVEL: 100,
  XP_PER_LEVEL: 1000,
};
```

### 🔄 **Real-time Updates**

#### **WebSocket Events** (if implemented)
```typescript
interface WebSocketEvent {
  type: 'zone_update' | 'attack_event' | 'leaderboard_update';
  data: any;
  timestamp: string;
}

// Zone Update Event
interface ZoneUpdateEvent {
  type: 'zone_update';
  data: {
    zone_id: string;
    owner_username?: string;
    is_claimed: boolean;
    expires_at?: string;
  };
}

// Attack Event
interface AttackEvent {
  type: 'attack_event';
  data: {
    zone_id: string;
    attacker_username: string;
    defender_username?: string;
    result: 'success' | 'failed';
    timestamp: string;
  };
}
```

### 📱 **Mobile App Integration Checklist**

#### **Authentication Flow**
- [ ] Implement secure token storage with `expo-secure-store`
- [ ] Set up automatic token refresh
- [ ] Handle login/logout state management
- [ ] Register FCM token on successful login

#### **Zone Management**
- [ ] Fetch nearby zones based on user location
- [ ] Implement zone claiming with location validation
- [ ] Show zone ownership status and expiry times
- [ ] Handle zone check-ins with success/error feedback

#### **Attack System**
- [ ] Implement attack functionality with location validation
- [ ] Show attack cooldown timers
- [ ] Display attack history and statistics
- [ ] Handle attack results with animations

#### **Push Notifications**
- [ ] Set up Firebase FCM client configuration
- [ ] Register for push notifications permissions
- [ ] Handle different notification types
- [ ] Navigate to relevant screens on notification tap

#### **Real-time Features**
- [ ] Listen for FCM notifications
- [ ] Update game state on notifications
- [ ] Show real-time zone status changes
- [ ] Handle background/foreground notification scenarios

#### **UI/UX Integration**
- [ ] Display zones on map with color coding
- [ ] Show user stats and level progression
- [ ] Implement leaderboard screens
- [ ] Add loading states and error handling
- [ ] Create success/failure feedback modals

---