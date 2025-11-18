import { BaseApi } from '../BaseApi'
import type { Tag } from './types'

export class TagsApi extends BaseApi {
  constructor() {
    super('/tags')
  }

  list() {
    return this.request<Tag, true>('/')
  }
}
