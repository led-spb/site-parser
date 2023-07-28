<template>
  <div class="q-pa-sm" style="min-width: 360px; max-width: 360px;">
     <q-card flat bordered class="bg-grey-1">
        <q-item class="bg-secondary text-white">
          <q-item-section>
            <q-item-label>{{ item.spider }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <div class="q-gutter-xs"> <!--
              <q-btn size="12px" flat dense round icon="delete" color="grey-9"/>
              <q-btn size="12px" flat dense round icon="play_arrow" color="grey-9" @click="confirmRunJob = true"/> -->
              <q-btn size="12px" flat dense round icon="more_vert" color="grey-9"/>
            </div>
          </q-item-section>
        </q-item>
        <q-separator/>
        <q-list dense>
            <q-item>
              <q-item-section><q-item-label>{{ formatDate(item.created) }}</q-item-label></q-item-section>
            </q-item>
        </q-list>
        <q-separator/>
        <q-card-section>
          <span v-html="formatBody(item.formatted)"/>
        </q-card-section>
     </q-card>
  </div>
</template>

<script>

import { ref, defineComponent } from 'vue'
import { date } from 'quasar'
import { useItemStore } from 'stores/itemStore'
import { mapActions } from 'pinia'
var humanize = require('humanize');


export default defineComponent({
  name: 'ItemCard',

  props: [
    'item'
  ],
  computed: {
    formatDate(){
      return (value) => {
          return date.formatDate(value, "DD.MM.YYYY HH:mm:ss")
      }
    },
    formatBody(){
      return (value) => {
           return value.replaceAll('\n','<br>')
      }
    }
  },
  methods: {
  },
  data() {
    return {}
  },
  setup () {
    return {
      humanize
    }
  }
})
</script>
