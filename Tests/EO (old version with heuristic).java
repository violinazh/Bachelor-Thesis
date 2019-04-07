package com.violina;

import org.springframework.util.StopWatch;

import java.util.*;

public class EqualityOperator {

    private int start_point; // the vid of the start point given by the user
    private List<Integer> categories; // the set of categories, given by the user
    // equal indices
    private int i;
    private int j;
    private NearestNeighbor [][] table;
    private Graph graph;
    private KNN knn;
    private Route firstPSR;

    private PriorityQueue<Route> heap;
    private double UB; // upper bound variable

    private StopWatch stopWatch;
    private long duration = 0; // Processing time for KNN

    private long time = 0; // Processing time
    private long time_PNE = 0; // Processing time for PNE
    private int counter_heap = 0; // Number of heap fetches
    private Route optimalRoute; // route found with PNE

    public EqualityOperator(int sp, List<Integer> categories, int [] equal, NearestNeighbor [][] table, Graph graph) {
        this.start_point = sp;
        this.categories = categories;
        this.i = equal[0];
        this.j = equal[1];
        this.table = table;
        this.graph = graph;
        knn = new KNN(graph);
        firstPSR = new Route();

        int initialCapacity = 15;
        Comparator<Route> comparator = new Comparator<Route>() {
            @Override
            public int compare(Route e1, Route e2) {
                return Double.compare(e1.getLength() + e1.getHeuristic(), e2.getLength() + e2.getHeuristic());
            }
        };
        heap = new PriorityQueue<Route>(initialCapacity, comparator);

        UB = 0;
        stopWatch = new StopWatch();

    }

    public long getTime() {
        return time;
    }

    public long getTime_PNE() {
        return time_PNE;
    }

    public int getCounter_heap() {
        return counter_heap;
    }

    public Route getOptimalRoute() {
        return optimalRoute;
    }


    public Route equality_algorithm () {

        stopWatch.start();  //start stopwatch

        // Check if the indices can be equal
        if (categories.get(i) != categories.get(j)) {
            System.out.println("Not possible indices!!!");

            stopWatch.stop();  //stop stopwatch
            return null;
        }

        PNE pne = new PNE(start_point, categories, table, graph);
        optimalRoute = pne.pne_algorithm();
        time_PNE = pne.getTime();

        if (optimalRoute.getRpoi(i).getPid() == optimalRoute.getRpoi(j).getPid()) {
            // Optimal route has been found
            System.out.println("Found optimal route with PNE");

            stopWatch.stop();  //stop stopwatch
            time = stopWatch.getTotalTimeMillis() - (duration/1000000);
            return optimalRoute;
        } else {
            System.out.println("Modifying route");

            /* Old version - optimal route is not always found this way
            // firstPSR
            for (int k = 0; k < i; k++) {
                firstPSR.addRpoi(optimalRoute.getRpoi(k));
            }
            //System.out.println("First PSR: " + firstPSR);*/

            // dummySR
            dummySR(optimalRoute);

            return modifiedPNE();
        }

    }

    private void dummySR(Route optimalRoute) {
        Route dummySR = new Route();
        for (int k = 0; k < j; k++) { // adding the PoIs until r_j; !!! if i = 0 there won't be any PoIs to add
            dummySR.addRpoi(optimalRoute.getRpoi(k));
        }

        // Finding the distance between r_{j-1} and r_i
        knn.dijkstra(graph.getNode(dummySR.getRpoi(j - 1).getVid()));
        double dist = knn.getLength(dummySR.getRpoi(i).getVid());
        R_POI rpoi = new R_POI(dummySR.getRpoi(i).getPid(), dummySR.getRpoi(i).getVid(), dummySR.getRpoi(i).getType(), dist);
        dummySR.addRpoi(rpoi);

        if (j < categories.size() - 1) { // Checking if j is the last PoI
            List<Integer> categoriesAfterJ = new ArrayList<>();
            for (int k = j + 1; k < categories.size(); k++) {
                categoriesAfterJ.add(categories.get(k));
            }
            PNE pneAfterJ = new PNE(dummySR.getRpoi(i).getVid(), categoriesAfterJ, table, graph);
            Route routeAfterJ = pneAfterJ.pne_algorithm();
            for (R_POI p: routeAfterJ.getPois()) {
                dummySR.addRpoi(p);
            }
        }
        //System.out.println("Dummy SR: " + dummySR);

        // Placing dummySR on the heap
        max(dummySR); // calculating the heuristic;  0 in this case
        UB = dummySR.getLength(); // initializing the upper bound
        heap.add(dummySR);

    }

    // Version with heuristic
    private Route modifiedPNE() {

        // First part: Adding all neighbours to the sp
        long s = System.nanoTime();
        knn.dijkstra(graph.getNode(start_point));
        for (Node node : graph.getNodes()) {
            for (PoI poi : node.getPoIs()) {
                if (poi.getType() == categories.get(0)) {

                    Route route = new Route();
                    R_POI rpoi = new R_POI(poi.getPid(), node.getId(), categories.get(0), knn.getLength(node.getId()));
                    route.addRpoi(rpoi);
                    max(route); // Calculating the heuristic

                    // Checking the lower bound
                    double LB = route.getLength() + route.getHeuristic();
                    if (LB <= UB) {
                        heap.add(route);
                    }
                }
            }
        }
        long e = System.nanoTime();
        //System.out.println("Neighbor time: " + (e - s)/1000000);


        // Second part: modified PNE

        Route candidate = new Route();

        // fetching a PSR from the heap
        Route current = heap.poll();
        counter_heap++;

        while (current.size() < categories.size()) {

            //System.out.println("Current: " + current + ", Heuristic: " + current.getHeuristic());
            int l = current.size();
            //System.out.println("Size: " + l);

            case1:
            {
                if (l <= j - 1) { // Finding PSRs before r_j
                    // (a)
                    // Checking the lower bound; only in a)
                    double LB_A = current.getLength() + current.getHeuristic();
                    if (LB_A <= UB) { // we check the heuristic after fetching the route
                        Route newA = modifyRouteA(current, "nn");
                        if (!heap.contains(newA)) {
                            heap.add(newA);
                        }
                        //System.out.println("NewA: " + newA);
                    } else {
                        //System.out.println("-> Break: NewA: " + newA + ", LB: " + LB_A);
                        // !!! Breaking would prevent b) from executing, but maybe it would generate a shorter route
                        //break case1;
                        // We don't do anything with the route; break
                    }

                    // We don't execute b) on the initial routes,
                    // because all of the possible neighbours have been added to the heap in the first step
                    if (l > 1) {
                        // (b)
                        Route newB = modifyRouteB(current, "nn");
                        ////System.out.println("NewB: " + newB);
                        if (newB != null) {
                            if (!heap.contains(newB)) {
                                heap.add(newB);
                            }
                        }
                    }
                }

            }

            case2:
            {
                if (l == j) { // Finding PSRs containing r_j
                    // (a), Finding the distance between r_{j-1} and r_i
                    // Checking the lower bound; only in a)
                    double LB_A = current.getLength() + current.getHeuristic();
                    if (LB_A <= UB) { // we check the heuristic after fetching the route
                        Route newA = modifyRouteA(current, "travel");
                        if (!heap.contains(newA)) {
                            // Trimming (only one candidate PSR on the heap)
                            trim(newA, candidate);
                        }
                        ////System.out.println("NewA: " + newA);
                    } else {
                        ////System.out.println("-> Break: NewA: " + newA + ", LB: " + LB_A);
                        // !!! Breaking would prevent b) from executing, but maybe it would generate a shorter route
                        //break case1;
                        // We don't do anything with the route; break
                    }

                    // (b)
                    Route newB = modifyRouteB(current, "nn");
                    ////System.out.println("NewB: " + newB);
                    if (newB != null) {
                        if (!heap.contains(newB)) {
                            heap.add(newB);
                        }
                    }
                }
            }

            case3:
            {
                if (l == j + 1) { // Finding PSRs containing/after r_j; only in case j is not the last element
                    // (a)
                    // Checking the lower bound; only in a)
                    double LB_A = current.getLength() + current.getHeuristic();
                    if (LB_A <= UB) { // we check the heuristic after fetching the route
                        Route newA = modifyRouteA(current, "nn");
                        if (!heap.contains(newA)) {
                            // Trimming (only one candidate PSR on the heap)
                            trim(newA, candidate);
                        }
                        ////System.out.println("NewA: " + newA);
                    } else {
                        ////System.out.println("-> Break: NewA: " + newA + ", LB: " + LB_A);
                        // !!! Breaking would prevent b) from executing, but maybe it would generate a shorter route
                        //break case1;
                        // We don't do anything with the route; break
                    }

                }
            }

            // Same as the PNE algorithm
            case4:
            {
                if (l >= j + 2) { // Finding PSRs after r_j; only in case j is not the last element
                    // (a)
                    // Checking the lower bound; only in a)
                    double LB_A = current.getLength() + current.getHeuristic();
                    if (LB_A <= UB) { // we check the heuristic after fetching the route
                        Route newA = modifyRouteA(current, "nn");
                        if (!heap.contains(newA)) {
                            // Trimming (only one candidate PSR on the heap)
                            trim(newA, candidate);
                        }
                        ////System.out.println("NewA: " + newA);
                    } else {
                        ////System.out.println("-> Break: NewA: " + newA + ", LB: " + LB_A);
                        // !!! Breaking would prevent b) from executing, but maybe it would generate a shorter route
                        //break case1;
                        // We don't do anything with the route; break
                    }

                    // (b)
                    Route newB = modifyRouteB(current, "nn");
                    ////System.out.println("NewB: " + newB);
                    if (newB != null) {
                        // Trimming not necessary - route's size is always less than categories.size()
                        if (!heap.contains(newB)) {
                            heap.add(newB);
                        }
                    }

                }
            }

            current = heap.poll();
            System.out.println("Current: " + current);
            counter_heap++;
        }


        stopWatch.stop();  //stop stopwatch
        //System.out.println("Duration for KNN: " + (duration/1000000) + " ms");
        time = stopWatch.getTotalTimeMillis() - (duration/1000000);
        //System.out.println("Time for the method: " + stopWatch.getTotalTimeMillis() + " ms"); ///get total time in ms

        // Optimal route with equal PoIs at i and j has been found
        return current;

    }

    private Route modifyRouteA(Route r, String how) {
        Route route = new Route(r);

        // Key
        int k;
        int vid;
        int index = route.size() - 1;
        if (index == -1) {
            vid = start_point;
        } else {
            vid = route.getRpoi(index).getVid();
        }
        Key key = new Key(vid, index);
        if (route.getNeighbors().containsKey(key)) {
            k = route.getNeighbors().get(key) + 1;
            route.putToMap(key, k);
        } else {
            k = 1;
            route.putToMap(key, k);
        }

        R_POI rpoi = null;
        switch (how) {

            case "travel":
                knn.dijkstra(graph.getNode(route.getRpoi(j - 1).getVid()));
                double dist = knn.getLength(route.getRpoi(i).getVid());
                rpoi = new R_POI(route.getRpoi(i).getPid(), route.getRpoi(i).getVid(), route.getRpoi(i).getType(), dist);
                break;

            case "nn":
                NearestNeighbor nn = getFirstNN(route.getPois().get(route.size() - 1).getVid(), categories.get(route.size()));
                rpoi = new R_POI(nn.getPid(), nn.getVid(), categories.get(route.size()), nn.getDist());
                break;

            default:
                System.out.println("We shouldn't be here!");
                break;
        }

        route.addRpoi(rpoi);
        max(route);
        return route;
    }

    private Route modifyRouteB(Route r, String how) {
        Route route = new Route(r);

        // Key
        int k;
        int vid;
        int index = route.size() - 2;
        if (index == -1) {
            vid = start_point;
        } else {
            vid = route.getRpoi(index).getVid();
        }
        Key key = new Key(vid, index);
        if (route.getNeighbors().containsKey(key)) {
            k = route.getNeighbors().get(key) + 1;
            route.putToMap(key, k);
        } else {
            k = 1;
            route.putToMap(key, k);
        }

        R_POI rpoi = null;
        switch (how) {

            case "travel":
                knn.dijkstra(graph.getNode(route.getRpoi(j - 1).getVid()));
                double dist = knn.getLength(route.getRpoi(i).getVid());
                rpoi = new R_POI(route.getRpoi(i).getPid(), route.getRpoi(i).getVid(), route.getRpoi(i).getType(), dist);
                break;

            case "nn":
                // Removing the processing time for KNN
                long startTime = System.nanoTime();
                NearestNeighbor nn = knn.knn(graph.getNode(vid), categories.get(index + 1), k);
                long endTime = System.nanoTime();
                duration += (endTime - startTime); //divide by 1000000 to get milliseconds
                if (nn != null) {
                    rpoi = new R_POI(nn.getPid(), nn.getVid(), categories.get(route.size() - 1), nn.getDist());
                } else {
                    return null;
                }
                break;

            default:
                System.out.println("We shouldn't be here!");
                break;
        }

        route.removeRpoi(route.size() - 1);
        route.addRpoi(rpoi);
        max(route);
        return route;

    }

    private void trim(Route route, Route candidate) {
        if (route.size() == categories.size()) {
            //System.out.println("!Trimming");
            // Update UB
            if (route.getLength() < UB) { // Check is not really necessary, because we check in modifiedPNE()
                //System.out.println("-> Updating UB");
                UB = route.getLength();
            }

            if (candidate.getLength() == 0) {
                candidate.setPois(route.getPois());
                candidate.setLength(route.getLength());
                candidate.setHeuristic(route.getHeuristic());
                if (!heap.contains(route)) {
                    heap.add(route);
                }
            } else if (route.getLength() < candidate.getLength()) {
                candidate.setPois(route.getPois());
                candidate.setLength(route.getLength());
                candidate.setHeuristic(route.getHeuristic());
                if (!heap.contains(route)) {
                    heap.add(route);
                }
            } else {
                // We don't add the new PSR
            }
        } else {
            if (!heap.contains(route)) {
                heap.add(route);
            }
        }
    }

    private NearestNeighbor getFirstNN(int vid, int category) {
        return table[vid][category];
    }

    // Calculates the maximum distance to the PoIs from all categories for the heuristic
    private void max (Route r) {
        double max = 0;
        int vid = r.getRpoi(r.size() - 1).getVid();
        for (int i = r.size(); i < categories.size(); i++) {
            if (r.size() > this.i + 1) { // heuristic should consider the distance between vertex_{r.size()-1} and r_i
                if (i == j) {
                    knn.dijkstra(graph.getNode(vid));
                    double dist = knn.getLength(r.getRpoi(this.i).getVid());
                    if (dist > max) {
                        max = dist;
                    }
                } else {
                    if (table[vid][categories.get(i)].getDist() > max) {
                        max = table[vid][categories.get(i)].getDist();
                    }
                }
            } else {
                if (table[vid][categories.get(i)].getDist() > max) {
                    max = table[vid][categories.get(i)].getDist();
                }
            }
        }
        r.setHeuristic(max);
    }

}

