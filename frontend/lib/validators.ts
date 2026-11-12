import type { ScoreRequest } from "@/types/scoring";

export type FormErrors = Partial<Record<keyof ScoreRequest, string>>;

export function validateScoreRequest(v: ScoreRequest): FormErrors {
  const e: FormErrors = {};
  if (!v.full_name.trim()) e.full_name = "Required";
  if (!/^\d{4}-\d{2}-\d{2}$/.test(v.date_of_birth)) e.date_of_birth = "Use YYYY-MM-DD";
  if (!/^[^@\s]+@[^@\s]+$/.test(v.email)) e.email = "Invalid email";
  if (v.phone.trim().length < 5) e.phone = "Too short";
  if (v.address.trim().length < 3) e.address = "Required";
  if (!v.device_id.trim()) e.device_id = "Required";
  if (!/^\d{1,3}(\.\d{1,3}){3}$/.test(v.ip_address)) e.ip_address = "Invalid IPv4";
  if (!(v.annual_income > 0)) e.annual_income = "Must be > 0";
  if (!(v.requested_credit > 0)) e.requested_credit = "Must be > 0";
  return e;
}
