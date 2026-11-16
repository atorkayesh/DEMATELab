import { useQuery } from "@tanstack/react-query";
import {
  HEALTH_QUERY_KEY,
  HEALTH_REFETCH_INTERVAL_MS,
} from "@/constants/health.constants";
import { getHealth } from "@/services/health.service";

export function useApiHealth() {
  return useQuery({
    queryKey: HEALTH_QUERY_KEY,
    queryFn: getHealth,
    refetchInterval: HEALTH_REFETCH_INTERVAL_MS,
    staleTime: 0,
  });
}
