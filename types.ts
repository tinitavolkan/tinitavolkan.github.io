
export interface Video {
  title: string;
  embed_id: string;
  link: string;
  parsedDate?: Date | null;
  category?: string;
}

export interface Category {
  id: string;
  name: string;
  icon?: string;
}
