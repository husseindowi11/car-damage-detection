import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { getInspections } from '@/services/api';
import type { InspectionListItem } from '@/types/api';

export default function InspectionsScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const [inspections, setInspections] = useState<InspectionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [total, setTotal] = useState(0);

  const loadInspections = async () => {
    try {
      setLoading(true);
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

  useEffect(() => {
    loadInspections();
  }, []);

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
    const colors = Colors[colorScheme ?? 'light'];
    
    return (
      <TouchableOpacity
        style={[styles.itemContainer, { backgroundColor: colors.background }]}
        onPress={() => router.push(`/inspection-detail?id=${item.id}`)}
        activeOpacity={0.7}
      >
        <ThemedView style={styles.itemContent}>
          <ThemedView style={styles.itemHeader}>
            <ThemedText type="defaultSemiBold" style={styles.carName}>
              {item.car_name}
            </ThemedText>
            <ThemedText style={[styles.cost, { color: colors.tint }]}>
              {formatCurrency(item.total_damage_cost)}
            </ThemedText>
          </ThemedView>
          
          <ThemedView style={styles.itemDetails}>
            <ThemedText style={styles.carInfo}>
              {item.car_model} • {item.car_year}
            </ThemedText>
            <ThemedText style={styles.date}>
              {formatDate(item.created_at)}
            </ThemedText>
          </ThemedView>
        </ThemedView>
      </TouchableOpacity>
    );
  };

  const colors = Colors[colorScheme ?? 'light'];

  if (loading && !refreshing) {
    return (
      <ThemedView style={styles.container}>
        <ActivityIndicator size="large" color={colors.tint} />
        <ThemedText style={styles.loadingText}>Loading inspections...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <ThemedView style={styles.header}>
        <ThemedText type="title" style={styles.title}>
          Inspections
        </ThemedText>
        <ThemedText style={styles.subtitle}>
          {total} {total === 1 ? 'inspection' : 'inspections'}
        </ThemedText>
      </ThemedView>

      {inspections.length === 0 ? (
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
  header: {
    padding: 20,
    paddingTop: 60,
    paddingBottom: 16,
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
  listContent: {
    padding: 16,
    paddingTop: 0,
  },
  itemContainer: {
    borderRadius: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  itemContent: {
    padding: 16,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  carName: {
    fontSize: 18,
    fontWeight: '600',
    flex: 1,
  },
  cost: {
    fontSize: 18,
    fontWeight: '700',
  },
  itemDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  carInfo: {
    fontSize: 14,
    opacity: 0.7,
  },
  date: {
    fontSize: 12,
    opacity: 0.5,
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
  loadingText: {
    marginTop: 12,
    opacity: 0.6,
  },
});

