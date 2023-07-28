<template>
  <div>
    <div class="fit row justify-center q-mt-sm">
      <q-pagination v-model="currentPage" :max="maxPage" :max-pages="6" v-if="maxPage > 1"/>
    </div>
    <q-select filled v-model="filterSpider" :options="spiderNames" label="Spider" stack-label dense options-dense />
    <div class="fit row justify-center">
      <item-card :item="item" v-for="item of items"/>
    </div>
  </div>
</template>

<script>
import { ref, defineComponent } from 'vue'
import { mapState } from 'pinia'
import { useItemStore } from 'stores/itemStore'
import { useSpiderStore } from 'stores/spiderStore'
import ItemCard from 'components/ItemCardComponent.vue'



export default defineComponent({
  name: 'ItemsPage',

  props: {
    pagesize: {
      type: Number,
      default: 50
    }
  },

  components: {
    ItemCard
  },

  computed: {
    ...mapState(useItemStore, ['items']),
    ...mapState(useSpiderStore, ['spiderNames']),
    maxPage() {
      return (this.items.length / this.pagesize) >> 0;
    }
  },

  watch: {
    filterSpider(newValue, oldValue){
       useItemStore().loadItems(newValue)
    }
  },

  setup() {
     useSpiderStore().loadSpiders()
     useItemStore().loadItems()

     return {
        currentPage: ref(1),
        filterSpider: ref(null),
     }
  }
})
</script>
