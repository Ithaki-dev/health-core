#!/bin/bash

# Script para procesar emails automáticamente
# Se ejecuta cada 2 minutos

cd /home/frappe/frappe-bench

while true; do
    echo "$(date): Processing email queue..."
    
    # Procesar emails pendientes
    bench --site 4geeks execute "frappe.email.queue.flush"
    
    # Esperar 2 minutos (120 segundos)
    sleep 120
done