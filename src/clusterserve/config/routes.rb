Clusterserve::Application.routes.draw do
  resources :feature_values
  resources :classifications
  resources :runs do
    resources :clusters, shallow: true
  end

  resources :experiments

  root to: 'runs#index'

end
