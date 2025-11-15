import React, { useState } from 'react';
import {
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  TextInput,
  View,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { submitInspection } from '@/services/api';
import { Image } from 'expo-image';
import { IconSymbol } from '@/components/ui/icon-symbol';

type ImageType = 'before' | 'after';

export default function InspectScreen() {
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];

  const [carName, setCarName] = useState('');
  const [carModel, setCarModel] = useState('');
  const [carYear, setCarYear] = useState('');
  const [beforeImages, setBeforeImages] = useState<string[]>([]);
  const [afterImages, setAfterImages] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  // Request camera and media library permissions
  const requestPermissions = async () => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: mediaStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (cameraStatus !== 'granted' || mediaStatus !== 'granted') {
      Alert.alert(
        'Permissions Required',
        'Please grant camera and media library permissions to use this feature.'
      );
      return false;
    }
    return true;
  };

  const pickImage = async (type: ImageType, source: 'camera' | 'library') => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    let result: ImagePicker.ImagePickerResult;

    if (source === 'camera') {
      result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });
    } else {
      result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: true,
        allowsEditing: false,
        quality: 0.8,
      });
    }

    if (!result.canceled) {
      const uris = result.assets.map((asset) => asset.uri);
      
      if (type === 'before') {
        setBeforeImages([...beforeImages, ...uris]);
      } else {
        setAfterImages([...afterImages, ...uris]);
      }
    }
  };

  const removeImage = (type: ImageType, index: number) => {
    if (type === 'before') {
      setBeforeImages(beforeImages.filter((_, i) => i !== index));
    } else {
      setAfterImages(afterImages.filter((_, i) => i !== index));
    }
  };

  const validateForm = (): boolean => {
    if (!carName.trim()) {
      Alert.alert('Validation Error', 'Please enter car name');
      return false;
    }
    if (!carModel.trim()) {
      Alert.alert('Validation Error', 'Please enter car model');
      return false;
    }
    const year = parseInt(carYear);
    if (!carYear || isNaN(year) || year < 1900 || year > 2100) {
      Alert.alert('Validation Error', 'Please enter a valid year (1900-2100)');
      return false;
    }
    if (beforeImages.length === 0) {
      Alert.alert('Validation Error', 'Please add at least one BEFORE image');
      return false;
    }
    if (afterImages.length === 0) {
      Alert.alert('Validation Error', 'Please add at least one AFTER image');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setSubmitting(true);
      const response = await submitInspection(
        carName.trim(),
        carModel.trim(),
        parseInt(carYear),
        beforeImages,
        afterImages
      );

      if (response.success) {
        Alert.alert(
          'Success',
          'Inspection submitted successfully!',
          [
            {
              text: 'OK',
              onPress: () => {
                // Reset form
                setCarName('');
                setCarModel('');
                setCarYear('');
                setBeforeImages([]);
                setAfterImages([]);
              },
            },
          ]
        );
      }
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.message || 'Failed to submit inspection. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const renderImageSection = (
    type: ImageType,
    images: string[],
    title: string
  ) => {
    return (
      <ThemedView style={styles.imageSection}>
        <ThemedText style={styles.sectionTitle}>{title}</ThemedText>
        <ThemedText style={styles.sectionSubtitle}>
          {images.length} {images.length === 1 ? 'image' : 'images'} added
        </ThemedText>

        {/* Image Grid */}
        {images.length > 0 && (
          <View style={styles.imageGrid}>
            {images.map((uri, index) => (
              <View key={index} style={styles.imageWrapper}>
                <Image source={{ uri }} style={styles.image} contentFit="cover" />
                <TouchableOpacity
                  style={styles.removeButton}
                  onPress={() => removeImage(type, index)}
                >
                  <IconSymbol name="xmark.circle.fill" size={24} color="#EF4444" />
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}

        {/* Action Buttons */}
        <View style={styles.imageActions}>
          <TouchableOpacity
            style={[styles.imageButton, { backgroundColor: colors.tint }]}
            onPress={() => pickImage(type, 'camera')}
          >
            <IconSymbol name="camera.fill" size={20} color="#fff" />
            <ThemedText style={styles.imageButtonText}>Take Photo</ThemedText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.imageButton, styles.imageButtonSecondary, { borderColor: colors.tint }]}
            onPress={() => pickImage(type, 'library')}
          >
            <IconSymbol name="photo.fill" size={20} color={colors.tint} />
            <ThemedText style={[styles.imageButtonText, { color: colors.tint }]}>
              Choose from Library
            </ThemedText>
          </TouchableOpacity>
        </View>
      </ThemedView>
    );
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>
            New Inspection
          </ThemedText>
          <ThemedText style={styles.subtitle}>
            Fill in the car details and add images
          </ThemedText>
        </ThemedView>

        {/* Form */}
        <ThemedView style={styles.form}>
          <ThemedView style={styles.formSection}>
            <ThemedText style={styles.label}>Car Name *</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, borderColor: colors.icon + '40' }]}
              placeholder="e.g., Toyota Corolla"
              placeholderTextColor={colors.icon + '80'}
              value={carName}
              onChangeText={setCarName}
            />
          </ThemedView>

          <ThemedView style={styles.formSection}>
            <ThemedText style={styles.label}>Car Model *</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, borderColor: colors.icon + '40' }]}
              placeholder="e.g., SE, GLS, Sport"
              placeholderTextColor={colors.icon + '80'}
              value={carModel}
              onChangeText={setCarModel}
            />
          </ThemedView>

          <ThemedView style={styles.formSection}>
            <ThemedText style={styles.label}>Car Year *</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, borderColor: colors.icon + '40' }]}
              placeholder="e.g., 2020"
              placeholderTextColor={colors.icon + '80'}
              value={carYear}
              onChangeText={setCarYear}
              keyboardType="numeric"
              maxLength={4}
            />
          </ThemedView>
        </ThemedView>

        {/* Before Images */}
        {renderImageSection('before', beforeImages, 'BEFORE Images')}

        {/* After Images */}
        {renderImageSection('after', afterImages, 'AFTER Images')}

        {/* Submit Button */}
        <TouchableOpacity
          style={[
            styles.submitButton,
            { backgroundColor: colors.tint },
            submitting && styles.submitButtonDisabled,
          ]}
          onPress={handleSubmit}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <IconSymbol name="checkmark.circle.fill" size={20} color="#fff" />
              <ThemedText style={styles.submitButtonText}>Submit Inspection</ThemedText>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  header: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    opacity: 0.6,
  },
  form: {
    padding: 20,
  },
  formSection: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
  },
  imageSection: {
    padding: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    opacity: 0.6,
    marginBottom: 16,
  },
  imageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  imageWrapper: {
    position: 'relative',
    width: 100,
    height: 100,
    borderRadius: 12,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  removeButton: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 12,
  },
  imageActions: {
    flexDirection: 'row',
    gap: 12,
  },
  imageButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 14,
    borderRadius: 12,
    gap: 8,
  },
  imageButtonSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 2,
  },
  imageButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 18,
    marginHorizontal: 20,
    marginTop: 8,
    borderRadius: 16,
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
});

