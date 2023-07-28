import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export const useJobStore = defineStore('jobs', {
  state: () => ({
    jobs: []
  }),

  actions: {
    async loadJobs(){
        let response = await api.get('api/scheduler/jobs')
        this.jobs = response.data
    },

    async startJob(job_id){
        return (await api.post('api/scheduler/job/'+job_id, {'action': 'start'})).data
    },

    async getJobById(job_id){
        let job = (await api.get('api/scheduler/job/'+job_id)).data
        const itemIndex = this.jobs.findIndex((item) => {return item.id === job.id})
        if( itemIndex < 0 ){
            this.jobs.push(job)
        }else{
            this.jobs.splice(itemIndex, 1, job)
        }
        return job
    },

    async updateJob(job){
        let new_job = (await api.put('api/scheduler/job/'+job.id, job)).data
        const itemIndex = this.jobs.findIndex((item) => {return item.id === job.id})
        if( itemIndex < 0 ){
            this.jobs.push(new_job)
        }else{
            this.jobs.splice(itemIndex, 1, new_job)
        }


        return new_job
    },

    async createJob(job){
        let new_job = (await api.post('api/scheduler/jobs', job)).data
        const itemIndex = this.jobs.findIndex((item) => {return item.id === job.id})
        if( itemIndex < 0 ){
            this.jobs.push(new_job)
        }else{
            this.jobs.splice(itemIndex, 1, new_job)
        }

        return new_job
    },

    async removeJob(job_id){
        await api.delete('api/scheduler/job/'+job_id)
        this.jobs = this.jobs.filter((item) => {return item.id !== job_id } )
    }
  }
})
