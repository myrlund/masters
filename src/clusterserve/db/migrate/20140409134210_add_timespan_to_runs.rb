class AddTimespanToRuns < ActiveRecord::Migration
  def change
    add_column :runs, :timespan_from, :integer
    add_column :runs, :timespan_to, :integer
  end
end
