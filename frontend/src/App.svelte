<script>
  import { Router, Route } from "svelte-routing";
  import Login from "./pages/Login.svelte";
  import Admin from "./pages/Admin.svelte";
  import Estudiante from "./pages/Estudiante.svelte";
  import Docente from "./pages/Docente.svelte";

  export let url = "";
</script>

<Router {url}>
  <Route path="/" component={Login} />
  <Route path="/admin" component={Admin} />
  <Route path="/estudiante" component={Estudiante} />
  <Route path="/docente" component={Docente} />
</Router>
