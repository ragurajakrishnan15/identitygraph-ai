export type Tier = "Low" | "Medium" | "High";

export interface Factor {
  feature: string;
  description: string;
  contribution: number;
  direction: string;
}

export interface ScoreInfo {
  application_id: string;
  score: number;
  display_score: number;
  tier: Tier;
  recommendation: string;
  model_version: string;
  scored_at: string;
  factors: Factor[];
}

export interface LinkedEntity {
  entity_id: string;
  kind: string;
  label: string;
  shared_with_other_applications: number;
}

export interface Application {
  application_id: string;
  applicant_id: string;
  application_timestamp: string;
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
  fraud_label: number | null;
  fraud_scenario: string | null;
  source: string;
  split: string | null;
  score: ScoreInfo | null;
  linked_entities?: LinkedEntity[];
  notes?: { id: number; note: string; created_at: string }[];
  timeline?: { event: string; at: string }[];
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Overview {
  total: number;
  tiers: Partial<Record<Tier, number>>;
  avg_score: number;
  channels: { channel: string; tier: Tier; count: number }[];
  trend: { period: string; applications: number; avg_score: number }[];
  top_cases: Application[];
}
