import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export const useItemStore = defineStore('items', {
  state: () => ({
    items: []
  }),

  getters: {
  },

  actions: {
    async loadItems(spider){
        let response = await (spider? api.get('api/items', {params: {spider: spider}}) : api.get('api/items'))
        console.log(response)
        this.items = response.data
    },
  }
})

