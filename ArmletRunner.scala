package armlet

import scala.io.Source

object ArmletRunner:

  def main(args: Array[String]): Unit =
    if args.length < 1 then
      println("Usage: ArmletRunner <program.s>")
      sys.exit(1)

    val filename = args(0)
    val source = Source.fromFile(filename).mkString

    // Assemble
    val (binOpt, msg) = assemble(source)

    if binOpt.isEmpty then
      println("ASSEMBLY_ERROR")
      println(msg)
      sys.exit(1)

    val bin = binOpt.get

    // Build machine
    val machine = new armletPackage()
    machine.loadBinAndReset(bin)

    // Run until halt or trap
    while !machine.hlt_e.value && !machine.trp_e.value do
      machine.clock()

    // Print final state in easy-to-parse format
    println("===REGISTERS===")

    val status = machine.status
    val lines = status.split("\n")

    for line <- lines do
      if line.startsWith("$") then
        // Example: $2:  0000000000000000
        val parts = line.split(":")
        val reg = parts(0).trim
        val valueBits = parts(1).trim

        val value = armlet.bitsToInt(
          valueBits.reverse.map(_ == '1').toArray
        )

        println(s"$reg=$value")

    println("===END===")

