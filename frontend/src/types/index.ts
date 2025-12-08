/**
 * Type definitions for the Scanity frontend application
 */

export type IssueCategory = 'security' | 'performance' | 'quality';
export type IssueSeverity = 'HIGH' | 'MEDIUM' | 'LOW';
export type ScanStatus = 'pending' | 'scanning' | 'completed' | 'failed';

export interface Issue {
  id: string;
  category: IssueCategory;
  severity: IssueSeverity;
  title: string;
  description: string;
  impact: string;
  fix_steps: string[];
  estimated_time: string;
  code_example?: string;
  affected_resources?: string[];
}

export interface CategoryResult {
  score: number;
  issues_count: number;
  issues: Issue[];
}

export interface PerformanceMetrics {
  page_load_time: number;
  total_size_kb: number;
  requests_count: number;
  lcp?: number;
  fid?: number;
  cls?: number;
  ttfb?: number;
}

export interface ScanResult {
  scan_id: string;
  url: string;
  status: ScanStatus;
  health_score: number;
  categories: {
    security: CategoryResult;
    performance: CategoryResult;
    quality: CategoryResult;
  };
  metrics: PerformanceMetrics | null;
  screenshot_url?: string;
  created_at: string;
  error_message?: string;
  ai_summary?: AISummary;
}

export interface AISummary {
  ai_generated: boolean;
  health_score: number;
  overall_status: string;
  summary: string;
  key_strengths: string[];
  critical_issues: string[];
  recommendations: Recommendation[];
  next_steps: string[];
}

export interface Recommendation {
  priority: 'High' | 'Medium' | 'Low';
  action: string;
  reason: string;
}

export interface ScanRequest {
  url: string;
  options: ScanOptions;
}

export interface ScanOptions {
  include_screenshot: boolean;
  scan_depth: 'quick' | 'standard' | 'deep';
  mobile_view: boolean;
}

export interface ScanResponse {
  scan_id: string;
  status: string;
  estimated_time: number;
}

export interface HealthResponse {
  status: string;
  ollama_status: string;
  version: string;
  timestamp?: string;
}

export interface APIError {
  success: false;
  error: string;
  error_code?: string;
  details?: Record<string, any>;
}

export interface APISuccess<T = any> {
  success: true;
  message: string;
  data?: T;
}

// Component Props Types
export interface ScanInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
  error?: string;
}

export interface ScanButtonProps {
  onClick: () => void;
  loading?: boolean;
  disabled?: boolean;
}

export interface ScanProgressProps {
  progress: number;
  currentStep: string;
  onCancel?: () => void;
}

export interface HealthScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
}

export interface IssueCardProps {
  issue: Issue;
  expanded?: boolean;
  onToggle?: () => void;
  onCopyCode?: (code: string) => void;
}

export interface CategorySectionProps {
  category: IssueCategory;
  result: CategoryResult;
  onToggleAll?: () => void;
  allExpanded?: boolean;
}

export interface ResultsDashboardProps {
  result: ScanResult;
  onExportPDF?: () => void;
  onShare?: () => void;
}

export interface PDFExportButtonProps {
  scanId: string;
  disabled?: boolean;
}

// Hook Types
export interface UseScanReturn {
  scanState: ScanStatus;
  currentScan: ScanResult | null;
  progress: number;
  error: string | null;
  startScan: (url: string, options?: ScanOptions) => Promise<void>;
  cancelScan: () => void;
  getResults: (scanId: string) => Promise<ScanResult | null>;
  resetScan: () => void;
}

export interface UsePDFExportReturn {
  exportPDF: (scanId: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

// UI State Types
export interface ThemeContextType {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export interface NotificationType {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

// Form Types
export interface ValidationError {
  field: string;
  message: string;
}

export interface FormState<T> {
  values: T;
  errors: ValidationError[];
  touched: Record<keyof T, boolean>;
  isValid: boolean;
  isSubmitting: boolean;
}

// Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface FilterOptions {
  category?: IssueCategory;
  severity?: IssueSeverity;
  search?: string;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}

// Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Event Types
export interface ScanEvent {
  type: 'start' | 'progress' | 'complete' | 'error';
  scanId: string;
  data?: any;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: any;
}