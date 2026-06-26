import apiClient from '@/lib/api-client';

export async function updateStreak() {
  return apiClient.request<{ current_streak: number; longest_streak: number; updated: boolean }>(
    '/api/gamification/streak/update',
    { method: 'POST' }
  );
}

export async function getStreak() {
  return apiClient.request<{ current_streak: number; longest_streak: number }>(
    '/api/gamification/streak'
  );
}

export async function addPoints(points: number) {
  return apiClient.request<{ total_points: number }>(
    `/api/gamification/points/add?points=${points}`,
    { method: 'POST' }
  );
}

export async function addXp(xp: number) {
  return apiClient.request<{ level: number; xp: number; leveled_up: boolean }>(
    `/api/avatar/add-xp?xp=${xp}`,
    { method: 'POST' }
  );
}

export async function getAvatar() {
  return apiClient.request<{ user_id: number; level: number; xp: number }>(
    '/api/avatar/'
  );
}

export async function openMysteryBox(boxId: string) {
  return apiClient.request<{ type: string; value: number; message: string }>(
    '/api/mystery-box/open',
    { method: 'POST', body: JSON.stringify({ box_id: boxId }) }
  );
}

export async function createMysteryBox(rarity: string) {
  return apiClient.request<{ id: string; user_id: number; rarity: string; opened: boolean }>(
    `/api/mystery-box/create?rarity=${rarity}`,
    { method: 'POST' }
  );
}

export async function getNextActions(lastAction: string) {
  return apiClient.request<{ actions: Array<{ title: string; action: string; icon: string; points: number }> }>(
    '/api/phase1/next-actions',
    { method: 'POST', body: JSON.stringify({ last_action: lastAction }) }
  );
}

export async function updateCombo(success: boolean) {
  return apiClient.request<{ multiplier: number; points_earned: number; combo_count: number; message: string }>(
    '/api/phase1/combo',
    { method: 'POST', body: JSON.stringify({ success }) }
  );
}
