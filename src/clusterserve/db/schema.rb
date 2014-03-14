# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20140313164153) do

  create_table "classifications", force: true do |t|
    t.string   "person"
    t.integer  "cluster_id"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "classifications", ["cluster_id"], name: "index_classifications_on_cluster_id", using: :btree

  create_table "cluster_statistics", force: true do |t|
    t.integer  "cluster_id"
    t.string   "feature"
    t.decimal  "number",             precision: 10, scale: 0
    t.decimal  "sum",                precision: 10, scale: 0
    t.decimal  "variance",           precision: 10, scale: 0
    t.decimal  "standard_deviation", precision: 10, scale: 0
    t.decimal  "min",                precision: 10, scale: 0
    t.decimal  "max",                precision: 10, scale: 0
    t.decimal  "mean",               precision: 10, scale: 0
    t.decimal  "mode",               precision: 10, scale: 0
    t.decimal  "median",             precision: 10, scale: 0
    t.decimal  "range",              precision: 10, scale: 0
    t.decimal  "q1",                 precision: 10, scale: 0
    t.decimal  "q2",                 precision: 10, scale: 0
    t.decimal  "q3",                 precision: 10, scale: 0
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "cluster_statistics", ["cluster_id"], name: "index_cluster_statistics_on_cluster_id", using: :btree

  create_table "clusters", force: true do |t|
    t.integer  "run_id"
    t.text     "center"
    t.string   "label"
    t.decimal  "variance",   precision: 10, scale: 0
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "clusters", ["run_id"], name: "index_clusters_on_run_id", using: :btree

  create_table "events_raw", force: true do |t|
    t.string  "raw_event", limit: 250
    t.integer "timestamp"
    t.string  "person",    limit: 120
    t.text    "raw_json"
  end

  add_index "events_raw", ["person"], name: "person", using: :btree

  create_table "events_ref", primary_key: "raw_id", force: true do |t|
    t.string  "person",       limit: 120, null: false
    t.integer "timestamp",                null: false
    t.string  "event_type",   limit: 100, null: false
    t.string  "event_verb",   limit: 150
    t.string  "event_object", limit: 150
    t.string  "roomname",     limit: 200
    t.string  "url",          limit: 200
  end

  add_index "events_ref", ["person", "timestamp", "event_type", "roomname"], name: "person", using: :btree

  create_table "events_ref_omitted", primary_key: "raw_id", force: true do |t|
    t.integer "timestamp"
  end

  add_index "events_ref_omitted", ["timestamp"], name: "timestamp", using: :btree

  create_table "feature_values", force: true do |t|
    t.integer  "classification_id"
    t.string   "feature"
    t.decimal  "value",             precision: 10, scale: 0
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "feature_values", ["classification_id"], name: "classification_id", using: :btree
  add_index "feature_values", ["classification_id"], name: "index_feature_values_on_classification_id", using: :btree
  add_index "feature_values", ["feature"], name: "index_feature_values_on_feature", using: :btree

  create_table "room_presences", force: true do |t|
    t.string  "person",    limit: 120
    t.integer "timestamp"
    t.string  "roomname",  limit: 200
  end

  add_index "room_presences", ["person"], name: "person", using: :btree
  add_index "room_presences", ["roomname"], name: "roomname", using: :btree
  add_index "room_presences", ["timestamp"], name: "timestamp", using: :btree

  create_table "runs", force: true do |t|
    t.string   "algorithm"
    t.string   "params"
    t.text     "features"
    t.text     "comment"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "user_graph", id: false, force: true do |t|
    t.string  "person1", limit: 120, null: false
    t.string  "person2", limit: 120, null: false
    t.integer "weight",              null: false
  end

  create_table "user_models", id: false, force: true do |t|
    t.string "person",  limit: 120, default: "", null: false
    t.string "feature", limit: 150, default: "", null: false
    t.float  "value"
  end

end
