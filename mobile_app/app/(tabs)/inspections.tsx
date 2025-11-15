import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
  View,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { PageHeader } from '@/components/page-header';
import { Colors } from '@/constants/theme';
import { getInspections } from '@/services/api';
import type { InspectionListItem } from '@/types/api';

export default function InspectionsScreen() {
  const router = useRouter();
  const [inspections, setInspections] = useState<InspectionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [total, setTotal] = useState(0);

  const loadInspections = async (showLoading: boolean = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const response = await getInspections(0, 100);
      if (response.status && response.data) {
        setInspections(response.data.inspections);
        setTotal(response.data.total);
      }
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.message || 'Failed to load inspections'
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Load inspections on mount
  useEffect(() => {
    loadInspections(true);
  }, []);

  // Reload inspections silently when screen comes into focus (preserves scroll position)
  useFocusEffect(
    React.useCallback(() => {
      // Only reload if not the initial mount (inspections already loaded)
      if (inspections.length > 0) {
        loadInspections(false);
      }
    }, [inspections.length])
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadInspections();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const renderInspectionItem = ({ item }: { item: InspectionListItem }) => {
    const colors = Colors.light;
    
    return (
      <TouchableOpacity
        style={styles.itemContainer}
        onPress={() => router.push(`/inspection-detail?id=${item.id}`)}
        activeOpacity={0.7}
      >
        <View style={[styles.itemContent, { backgroundColor: colors.background }]}>
          <View style={styles.itemHeader}>
            <ThemedText type="defaultSemiBold" style={styles.carName}>
              {item.car_name}
            </ThemedText>
            <ThemedText style={[styles.cost, { color: colors.tint }]}>
              {formatCurrency(item.total_damage_cost)}
            </ThemedText>
          </View>
          
          <View style={styles.itemDetails}>
            <ThemedText style={styles.carInfo}>
              {item.car_model} • {item.car_year}
            </ThemedText>
            <ThemedText style={styles.date}>
              {formatDate(item.created_at)}
            </ThemedText>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const colors = Colors.light;

  return (
    <ThemedView style={styles.container}>
      <PageHeader 
        title="Inspections" 
        subtitle={`${total} ${total === 1 ? 'inspection' : 'inspections'}`}
      />
      
      {loading && !refreshing ? (
        <ThemedView style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.tint} />
          <ThemedText style={styles.loadingText}>Loading inspections...</ThemedText>
        </ThemedView>
      ) : inspections.length === 0 ? (
        <ThemedView style={styles.emptyContainer}>
          <ThemedText style={styles.emptyText}>No inspections yet</ThemedText>
          <ThemedText style={styles.emptySubtext}>
            Create your first inspection using the Inspect tab
          </ThemedText>
        </ThemedView>
      ) : (
        <FlatList
          data={inspections}
          renderItem={renderInspectionItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={colors.tint}
            />
          }
          showsVerticalScrollIndicator={false}
        />
      )}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listContent: {
    padding: 16,
    paddingTop: 8,
  },
  itemContainer: {
    borderRadius: 16,
    marginBottom: 16,
    // iOS shadow
    ...(Platform.OS === 'ios' && {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
    }),
    // Android elevation
    ...(Platform.OS === 'android' && {
      elevation: 3,
    }),
  },
  itemContent: {
    padding: 20,
    borderRadius: 16,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: 'transparent',
  },
  carName: {
    fontSize: 20,
    fontWeight: '700',
    flex: 1,
    marginRight: 12,
  },
  cost: {
    fontSize: 20,
    fontWeight: '800',
  },
  itemDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  carInfo: {
    fontSize: 15,
    opacity: 0.6,
    fontWeight: '500',
  },
  date: {
    fontSize: 13,
    opacity: 0.5,
    fontWeight: '400',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    opacity: 0.6,
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 12,
    opacity: 0.6,
    fontSize: 16,
  },
});

