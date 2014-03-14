class ClustersController < ApplicationController
  respond_to :json

  def index
    @run = Run.find(params[:run_id])
    @clusters = @run.clusters

    respond_with @clusters
  end
end
