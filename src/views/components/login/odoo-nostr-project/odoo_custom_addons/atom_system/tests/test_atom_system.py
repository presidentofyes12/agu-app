from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import time

@tagged('atom')
class TestAtomSystem(TransactionCase):

    def setUp(self):
        super(TestAtomSystem, self).setUp()
        self.atom_api = self.env['atom.api']
        self.element = self.env['atom.element'].create({
            'name': 'Test Element',
            'sequence': 1
        })

    def test_create_atom(self):
        atom = self.atom_api.create_atom({'name': 'Test Atom'})
        self.assertTrue(atom, "Atom should be created")
        self.assertEqual(atom.name, 'Test Atom', "Atom name should match")

    def test_read_atom(self):
        atom = self.atom_api.create_atom({'name': 'Test Atom'})
        read_atom = self.atom_api.read_atom(atom.id)
        self.assertEqual(read_atom[0]['name'], 'Test Atom', "Read atom should match created atom")

    def test_update_atom(self):
        atom = self.atom_api.create_atom({'name': 'Test Atom'})
        self.atom_api.update_atom(atom.id, {'name': 'Updated Atom'})
        updated_atom = self.atom_api.read_atom(atom.id)
        self.assertEqual(updated_atom[0]['name'], 'Updated Atom', "Atom name should be updated")

    def test_delete_atom(self):
        atom = self.atom_api.create_atom({'name': 'Test Atom'})
        self.atom_api.delete_atom(atom.id)
        with self.assertRaises(ValidationError):
            self.atom_api.read_atom(atom.id)

    def test_search_atoms(self):
        self.atom_api.create_atom({'name': 'Atom 1'})
        self.atom_api.create_atom({'name': 'Atom 2'})
        atoms = self.atom_api.search_atoms([('name', 'like', 'Atom')])
        self.assertEqual(len(atoms), 2, "Should find 2 atoms")

    def test_create_element_value(self):
        atom = self.atom_api.create_atom({'name': 'Test Atom'})
        value = self.atom_api.create_element_value(atom.id, self.element.id, {
            'value1': 1.0,
            'value2': 2.0,
            'value3': 3.0
        })
        self.assertEqual(value.sum, 6.0, "Sum should be calculated correctly")

    def test_advanced_search(self):
        atom1 = self.atom_api.create_atom({'name': 'Atom 1'})
        atom2 = self.atom_api.create_atom({'name': 'Atom 2'})
        self.atom_api.create_element_value(atom1.id, self.element.id, {'value1': 1.0, 'value2': 2.0, 'value3': 3.0})
        self.atom_api.create_element_value(atom2.id, self.element.id, {'value1': 4.0, 'value2': 5.0, 'value3': 6.0})
        
        results = self.atom_api.advanced_search([
            {'element': 'Test Element', 'operator': '>', 'value': 3.0}
        ])
        self.assertEqual(len(results), 1, "Should find 1 atom")
        self.assertEqual(results[0].name, 'Atom 2', "Should find Atom 2")

    def test_performance_benchmark(self):
        start_time = time.time()
        for i in range(1000):
            self.atom_api.create_atom({'name': f'Benchmark Atom {i}'})
        end_time = time.time()
        duration = end_time - start_time
        self.assertLess(duration, 10, "Creating 1000 atoms should take less than 10 seconds")

@tagged('atom', 'integration')
class TestAtomIntegration(TransactionCase):

    def setUp(self):
        super(TestAtomIntegration, self).setUp()
        self.atom_api = self.env['atom.api']
        self.distributed_api = self.env['atom.distributed.api']

    def test_distributed_create(self):
        # This test assumes you have set up test distributed nodes
        result = self.distributed_api.distributed_create({'name': 'Distributed Atom'})
        self.assertTrue(result, "Distributed create should return a result")
        # Further assertions would depend on your specific implementation

    def test_conflict_resolution(self):
        atom = self.atom_api.create_atom({'name': 'Conflict Test Atom'})
        element = self.env['atom.element'].create({'name': 'Conflict Element', 'sequence': 2})
        self.atom_api.create_element_value(atom.id, element.id, {'value1': 1.0, 'value2': 2.0, 'value3': 3.0})

        conflict = self.env['atom.conflict.resolution'].resolve_conflict(
            atom.id, element.id,
            "1.0, 2.0, 3.0",
            "4.0, 5.0, 6.0"
        )
        self.assertEqual(conflict.resolution, 'manual', "Conflict should require manual resolution")

        # Simulate manual resolution
        conflict.write({
            'resolution': 'remote',
            'resolved_value': "4.0, 5.0, 6.0",
            'resolved_by': self.env.user.id,
            'resolved_date': fields.Datetime.now(),
        })

        # Check if the atom was updated with the resolved value
        updated_value = self.env['atom.element.value'].search([
            ('atom_id', '=', atom.id),
            ('element_id', '=', element.id)
        ])
        self.assertEqual(updated_value.value1, 4.0, "Atom should be updated with resolved value")