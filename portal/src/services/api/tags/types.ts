export interface Tag {
  id: number;
  name: string;
  slug: string;
  description: string;
  created_at: string;
}

export interface TagsResponse {
  data: Tag[];
}
