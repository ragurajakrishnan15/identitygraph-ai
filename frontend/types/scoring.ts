import type { Factor, Tier } from "./application";

export interface ScoreRequest {
  full_name: string;
  date_of_birth: string;
  email: string;
  phone: string;
  address: string;
  device_id: string;
  ip_address: string;
  employment_status: string;
  annual_income: number;
  requested_credit: number;
  application_channel: string;
}

export interface ScoreResponse {
  application_id: string;
  score: number;
  display_score: number;
  tier: Tier;
  recommendation: string;
  model_version: string;
  scored_at: string;
  top_factors: Factor[];
  linked_entities: { entity_id: string; kind: string; label: string; shared_with_other_applications: number }[];
  is_simulated: boolean;
  note: string;
}
