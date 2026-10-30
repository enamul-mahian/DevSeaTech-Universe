/**
 * Company constants. Public-facing contact details are fixed brand data;
 * URLs are environment-driven (the official domain is not yet hosted), so
 * apps should prefer process.env values and fall back to these.
 */
export const COMPANY = {
  name: "DevSeaTech",
  product: "DevSeaTech Universe",
  tagline: "Technology for a Safer Digital Tomorrow",
  phone: "+8801805839123",
  email: "devseatech60@gmail.com",
  website: "https://www.devseatech.com",
} as const;
