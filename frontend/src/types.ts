export type PIStatus = 'planning' | 'active' | 'closed';
export type FeatureStatus = 'funnel' | 'analyzing' | 'backlog' | 'implementing' | 'done';
export type ROAMStatus = 'unroamed' | 'owned' | 'accepted' | 'mitigated' | 'resolved';
export type DependencyStatus = 'identified' | 'owned' | 'accepted' | 'mitigated' | 'resolved';

export interface PI {
  id: string;
  name: string;
  art_id: string;
  start_date: string;
  end_date: string;
  iteration_ids: string[];
  status: PIStatus;
}

export interface Team {
  id: string;
  name: string;
  member_count: number;
  art_id: string | null;
}

export interface Iteration {
  id: string;
  pi_id: string;
  number: number;
  name: string;
  start_date: string;
  end_date: string;
  is_ip: boolean;
}

export interface Feature {
  id: string;
  name: string;
  description: string;
  pi_id: string | null;
  team_id: string | null;
  status: FeatureStatus;
  story_ids: string[];
  user_business_value: number;
  time_criticality: number;
  risk_reduction_opportunity_enablement: number;
  job_size: number;
  cost_of_delay: number;
  wsjf_score: number;
}

export interface Story {
  id: string;
  name: string;
  feature_id: string;
  team_id: string;
  iteration_id: string | null;
  points: number;
}

export interface Risk {
  id: string;
  description: string;
  pi_id: string;
  team_id: string | null;
  feature_id: string | null;
  roam_status: ROAMStatus;
  owner: string | null;
  mitigation_notes: string;
  raised_date: string;
}

export interface Dependency {
  id: string;
  description: string;
  pi_id: string;
  feature_id: string | null;
  from_team_id: string;
  to_team_id: string;
  iteration_id: string | null;
  status: DependencyStatus;
  owner: string | null;
  resolution_notes: string;
  raised_date: string;
  needed_by_date: string | null;
}
