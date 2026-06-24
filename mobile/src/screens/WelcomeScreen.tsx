import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import apiService from '../services/api';
import CONFIG from '../config';

/**
 * Welcome Screen
 *
 * First screen users see. Shows app info and connection status.
 */

export default function WelcomeScreen() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>(
    'checking'
  );
  const [backendVersion, setBackendVersion] = useState<string | null>(null);

  useEffect(() => {
    checkBackend();
  }, []);

  const checkBackend = async () => {
    setBackendStatus('checking');

    try {
      const health = await apiService.healthCheck();

      if (health.error) {
        throw new Error(health.error.message);
      }

      const version = await apiService.getVersion();

      setBackendStatus('connected');
      setBackendVersion(version.data?.version || 'unknown');
    } catch (error) {
      console.error('Backend connection failed:', error);
      setBackendStatus('error');
    }
  };

  const renderBackendStatus = () => {
    switch (backendStatus) {
      case 'checking':
        return (
          <View style={styles.statusContainer}>
            <ActivityIndicator color="#007AFF" />
            <Text style={styles.statusText}>Connecting to backend...</Text>
          </View>
        );

      case 'connected':
        return (
          <View style={styles.statusContainer}>
            <Text style={styles.statusIcon}>✅</Text>
            <Text style={styles.statusText}>Backend Connected</Text>
            {backendVersion && (
              <Text style={styles.versionText}>v{backendVersion}</Text>
            )}
          </View>
        );

      case 'error':
        return (
          <View style={styles.statusContainer}>
            <Text style={styles.statusIcon}>❌</Text>
            <Text style={[styles.statusText, styles.errorText]}>
              Cannot connect to backend
            </Text>
            <TouchableOpacity style={styles.retryButton} onPress={checkBackend}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
            <Text style={styles.helpText}>
              Make sure backend is running at:
              {'\n'}
              {CONFIG.API.BASE_URL}
            </Text>
          </View>
        );
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Xacari</Text>
        <Text style={styles.subtitle}>AI Workout Coach</Text>
      </View>

      {renderBackendStatus()}

      <View style={styles.infoContainer}>
        <Text style={styles.infoTitle}>Phase 2: Mobile Foundation</Text>
        <Text style={styles.infoText}>✅ React Native + Expo setup</Text>
        <Text style={styles.infoText}>✅ TypeScript configuration</Text>
        <Text style={styles.infoText}>✅ Supabase client ready</Text>
        <Text style={styles.infoText}>✅ Navigation structure</Text>
        <Text style={styles.infoText}>✅ State management (Zustand)</Text>
        <Text style={styles.infoText}>✅ WebSocket service</Text>
        <Text style={styles.infoText}>✅ API service</Text>
        <Text style={styles.infoText}>✅ Pose detection abstraction</Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Next Steps:{'\n'}
          • Update CONFIG with your local IP{'\n'}
          • Add Supabase credentials{'\n'}
          • Implement auth screens{'\n'}
          • Add camera & pose detection{'\n'}
          • Integrate custom RTMPose model
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 20,
    color: '#666',
  },
  statusContainer: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#FFF',
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  statusText: {
    fontSize: 16,
    color: '#333',
    marginTop: 8,
  },
  versionText: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
  },
  errorText: {
    color: '#FF3B30',
  },
  retryButton: {
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 20,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFF',
    fontWeight: '600',
  },
  helpText: {
    fontSize: 12,
    color: '#999',
    marginTop: 12,
    textAlign: 'center',
  },
  infoContainer: {
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
  },
  footer: {
    backgroundColor: '#FFF9E6',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  footerText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
});
