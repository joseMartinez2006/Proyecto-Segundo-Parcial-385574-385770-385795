// Ejecutar en el router mongos SOLO tras iniciar los cuatro replica sets.
// El write concern explicito es importante para shards de un unico miembro.
// Configurar el cluster distribuido para sample_mflix.movies

print("== Configurar write concern ==");
printjson(db.getSiblingDB("admin").runCommand({
  setDefaultRWConcern: 1,
  defaultWriteConcern: { w: 1 }
}));

print("== Agregar shards ==");

printjson(sh.addShard("shard1rs/shard1:27018"));
printjson(sh.addShard("shard2rs/shard2:27018"));
printjson(sh.addShard("shard3rs/shard3:27018"));

print("== Habilitar sharding en sample_mflix ==");

printjson(sh.enableSharding("sample_mflix"));

print("== Estado del cluster ==");

sh.status();