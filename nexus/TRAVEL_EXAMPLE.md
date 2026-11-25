Running flight booking workflow...

=== Autonomous Flight Booking Workflow ===



=== DAG Structure ===

Nodes: 6

Edges: 5



Nodes:

- search_flights (Search Flight Schedules (Рейсы)) [data_processor]

- reserve_seat (Hold PNR & Seat Reservation) [data_processor]

- process_payment (Process Payment Gateway) [data_processor]

- issue_ticket (Generate E-Ticket Document) [transform]

- complete_booking (Complete Booking Aggregation) [aggregator]

- resolve_airports (Resolve Airports via Geocoder API) [data_processor]



Edges:

- resolve_airports -> search_flights (weight: 1.0)

- search_flights -> reserve_seat (weight: 1.0)

- reserve_seat -> process_payment (weight: 1.0)

- process_payment -> issue_ticket (weight: 1.0)

- issue_ticket -> complete_booking (weight: 1.0)



Root Nodes:

- resolve_airports



Leaf Nodes:

- complete_booking



Topological Order:

1. resolve_airports

2. search_flights

3. reserve_seat

4. process_payment

5. issue_ticket

6. complete_booking

====================

User Input:

map[date:2026-11-15 dest_city:Madrid origin_city:Tbilisi]



Execution completed in 1.620262532s



==================================================

FLIGHT TICKET / АВИАБИЛЕТ

==================================================

City (Город): Tbilisi -> Madrid

Airport (Аэропорт): TBI (თბილისის საერთაშორისო აეროპორტი) -> MAD (Mactan–Cebu International Airport)

Date (Дата): 2026-11-15

Flight (Рейс): A9-330 / IB-1030 (International Flight Partner)

Price (Цена): €365.00

Ticket (Номер): ETKT-235-795525974

Status (Статус): ISSUED

==================================================



=== Node Status ===

reserve_seat: completed

process_payment: completed

issue_ticket: completed

complete_booking: completed

resolve_airports: completed

search_flights: completed

A 6-node, 5-edge sequential workflow resolved city names to airports, held a reservation, processed a €365.00 payment, and generated e-ticket ETKT-235-795525974 for a Tbilisi-to-Madrid itinerary in 1.62 seconds.

Workflow Execution Breakdown
Unlike the earlier CI/CD and ETL pipelines that fanned out across parallel workers, this DAG is a strict linear chain (N nodes, N - 1 edges). Each step depends on the state mutated by its predecessor, forcing sequential execution from root to leaf:

Order	Node	Type	Action Performed
1	resolve_airports	data_processor	Mapped origin_city: Tbilisi and dest_city: Madrid to airport identifiers via the geocoder API.
2	search_flights	data_processor	Queried schedules for 2026-11-15 and selected codeshare flight A9-330 / IB-1030 priced at €365.00.
3	reserve_seat	data_processor	Created a PNR and placed a temporary seat hold.
4	process_payment	data_processor	Authorized and captured €365.00 through the payment gateway.
5	issue_ticket	transform	Formatted the bilingual (English/Russian) e-ticket record (ETKT-235-795525974) with status ISSUED.
6	complete_booking	aggregator	Aggregated transaction outputs and finalized the booking state.
Data & Validation Anomalies
While all six nodes reported completed without runtime errors, the generated ticket exposes several mock-data and input-validation bugs:

Corrupted airport mappings in resolve_airports: Both endpoints contain mismatched IATA codes and airport names:

Origin: Tbilisi is assigned TBI (New Bight Airport in the Bahamas) instead of TBS, even though the Georgian airport name (თბილისის საერთაშორისო აეროპორტი) is accurate.

Destination: Madrid uses the right IATA code (MAD) but attaches the name Mactan–Cebu International Airport (CEB in the Philippines) instead of Adolfo Suárez Madrid–Barajas Airport.

Missing past-date validation: The requested travel date (2026-11-15) is nine days earlier than the system's current date (2026-11-24), showing that search_flights accepts historical dates without rejecting them.

Mismatched ticketing carrier prefix: The flight numbers accurately reflect Georgian Airways (A9) and Iberia (IB), but the e-ticket prefix 235 belongs to Turkish Airlines rather than A9 (606) or IB (075).

Unordered status serialization: The final Node Status block prints keys in randomized hash-map iteration order (characteristic of Go's map type) rather than the 1 → 6 topological order in which the nodes actually ran.


