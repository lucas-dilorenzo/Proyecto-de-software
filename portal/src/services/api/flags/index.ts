import { BaseApi } from '../BaseApi';
import type { Flag } from './types';

export class FlagsApi extends BaseApi {
  constructor() {
    super(''); // basePath vacío para usar solo API_BASE
  }

  async getStatus(): Promise<{ data: Flag }> {
    return this.request<{ data: Flag }>('/flags/status');
  }
}
