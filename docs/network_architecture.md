# Architecture réseau

## Datacenter principal

Localisation : Cotonou

## Pare-feu

Marque :
Fortinet FortiGate 200F

## VLAN

- VLAN 10 : Administration
- VLAN 20 : Développement
- VLAN 30 : Invités
- VLAN 40 : Production

## VPN

Tous les accès distants utilisent un VPN IPSec avec authentification MFA.

## Sauvegardes

Les sauvegardes sont réalisées chaque nuit à 02h00.

Rétention :
30 jours.