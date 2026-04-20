export interface Installation {
  id_item: string;
  name: string;
  topic_prefix: string;
  description: string | null;
  created_at: string;
}

export type CreateInstallationDTO = Pick<Installation, "name" | "description">;
