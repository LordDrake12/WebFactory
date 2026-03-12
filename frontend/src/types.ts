export type AuthResponse = {
  token: string;
  username: string;
};

export type WorldSummary = {
  id: number;
  code: string;
  name: string;
  owner_id: number;
  is_public: boolean;
  max_players: number;
  size_w: number;
  size_h: number;
  expansion_level: number;
};

export type WorldSnapshot = {
  world: WorldSummary;
  settings: Record<string, unknown>;
  state: {
    width: number;
    height: number;
    buildings: Array<{
      id: string;
      def_key: string;
      x: number;
      y: number;
      rotation: number;
    }>;
  };
};
