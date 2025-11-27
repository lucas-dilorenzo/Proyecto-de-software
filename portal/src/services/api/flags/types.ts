export interface Flag {
    maintenance_mode: boolean;
    reviews_enabled: boolean;
}

export interface TagsResponse {
  data: Flag;
}