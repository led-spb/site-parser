import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export const useSpiderStore = defineStore('spiders', {
  state: () => ({
    spiders: []
  }),

  getters: {
    spiderNames(state){
      return state.spiders.map(spider => spider.name)
    }
  },

  actions: {
    async loadSpiders(){
        if( this.spiders.length == 0){
          let response = await api.get('api/spiders')
          this.spiders = response.data
        }
    },

    spiderByName(name){
        return this.spiders.find(item => item.name == name)
    },
  }
})

